from __future__ import annotations

from automation.logging.step_logger import record_step_log
from automation.pages.etms.etms_catalogue_menu_page import (
    EtmsCatalogueMenuPage,
    etms_page_title_selectors,
    etms_sidebar_menu_selectors,
)


class EtmsDownloadControlPage(EtmsCatalogueMenuPage):
    """Performance page — sidebar navigation then wait for Download control enabled."""

    page_key: str
    page_hash: str
    title: str
    sidebar_menu_labels: tuple[str, ...] = ()
    menu_parent_label: str = ""
    performance_menu_suite: str = ""

    @property
    def page_title_selectors(self) -> list[str]:
        return etms_page_title_selectors(self.title)

    def _menu_selectors(self) -> list[str]:
        if self.menu_parent_label:
            return etms_sidebar_menu_selectors(
                self.menu_parent_label,
                self.sidebar_menu_labels or (self.title,),
                self.page_hash,
            )
        labels = self.sidebar_menu_labels or (self.title,)
        selectors: list[str] = []
        for label in labels:
            selectors.extend(
                [
                    f"xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='{label}']]",
                ]
            )
        selectors.append(f"a[href*='{self.page_hash}']")
        return list(dict.fromkeys(selectors))

    def _download_control_selectors(self) -> list[str]:
        return [
            (
                "xpath=//button["
                "(normalize-space()='Download' or .//span[normalize-space()='Download']) "
                "and not(@disabled) and not(contains(@class,'disabled'))]"
            ),
            (
                "xpath=//a["
                "(normalize-space()='Download' or .//span[normalize-space()='Download']) "
                "and not(@disabled) and not(contains(@class,'disabled'))]"
            ),
            (
                "xpath=//span[normalize-space()='Download']"
                "/ancestor::*[self::button or self::a][1]"
                "[not(@disabled) and not(contains(@class,'disabled'))]"
            ),
        ]

    def _is_on_page(self) -> bool:
        hash_fragment = self.page_hash.lower().replace("_", "-")
        return hash_fragment in self.current_url.lower().replace("_", "-")

    def is_download_enabled(self) -> bool:
        return self.find_visible(self._download_control_selectors()) is not None

    def _wait_for_download_enabled(self) -> None:
        self.wait_for_catalogue_idle()
        self.wait_for_page_stable()
        self.wait_for_enabled(
            self._download_control_selectors(),
            f"{self.title} Download control",
        )

    def _navigate_to_page(self) -> None:
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self.title} menu",
        )
        self._wait_for_url_hash(self.page_hash)
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.page_title_selectors,
            f"{self.title} page title",
        )

    def prepare_for_performance(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        first_page_step: bool = False,
    ) -> str:
        del tab_key, min_rows, allow_no_data, first_page_step
        return "page_load"

    def run_performance_measurement(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        mode: str = "page_load",
    ) -> None:
        del tab_key, min_rows, allow_no_data
        if mode == "skipped":
            return
        if mode == "page_load":
            self._navigate_to_page()
        self._wait_for_download_enabled()

    def confirm_grid_loaded(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
        allow_no_data: bool = False,
    ) -> EtmsDownloadControlPage:
        del min_rows, tab_key, allow_no_data
        self._wait_for_download_enabled()
        return self

    def wait_before_next_catalogue_navigation(self) -> EtmsDownloadControlPage:
        self.wait_for_catalogue_idle()
        self.wait_for_page_stable()
        return self

    def verify_performance_step(
        self,
        *,
        check_label: str,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
    ) -> int:
        del tab_key, min_rows, allow_no_data
        normalized_url = self.current_url.lower().replace("_", "-")
        assert self.page_hash in normalized_url, (
            f"{check_label} URL hash '{self.page_hash}' not found after navigation"
        )
        assert self.is_download_enabled(), (
            f"{check_label}: Download button/span must be enabled"
        )
        record_step_log(
            f"[PERF VERIFY] {check_label}: url OK, Download control enabled"
        )
        return 0
