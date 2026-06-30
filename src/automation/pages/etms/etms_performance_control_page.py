from __future__ import annotations

from automation.logging.step_logger import record_step_log
from automation.pages.etms.etms_catalogue_menu_page import (
    EtmsCatalogueMenuPage,
    etms_page_title_selectors,
    etms_sidebar_menu_selectors,
)


class EtmsPerformanceControlPage(EtmsCatalogueMenuPage):
    """Performance page that verifies enabled controls (no grid) after sidebar navigation."""

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
        labels = self.sidebar_menu_labels or (self.title,)
        return etms_sidebar_menu_selectors(
            self.menu_parent_label,
            labels,
            self.page_hash,
        )

    def _is_on_page(self) -> bool:
        hash_fragment = self.page_hash.lower().replace("_", "-")
        return hash_fragment in self.current_url.lower().replace("_", "-")

    def _control_selectors(self, control_key: str | None) -> list[str]:
        raise NotImplementedError

    def _control_label(self, control_key: str | None) -> str:
        raise NotImplementedError

    def is_control_enabled(self, control_key: str | None = None) -> bool:
        return self.find_visible(self._control_selectors(control_key)) is not None

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

    def _wait_for_control_enabled(self, control_key: str | None = None) -> None:
        label = self._control_label(control_key)
        self.wait_for_catalogue_idle()
        self.wait_for_page_stable()
        self.wait_for_enabled(
            self._control_selectors(control_key),
            f"{self.title} '{label}' control",
        )

    def prepare_for_performance(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        first_page_step: bool = False,
    ) -> str:
        del min_rows, allow_no_data
        if first_page_step or not self._is_on_page():
            return "page_load"
        return "control_check"

    def run_performance_measurement(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        mode: str = "page_load",
    ) -> None:
        del min_rows, allow_no_data
        if mode == "skipped":
            return
        if mode == "page_load":
            self._navigate_to_page()
        self._wait_for_control_enabled(tab_key)

    def confirm_grid_loaded(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
        allow_no_data: bool = False,
    ) -> EtmsPerformanceControlPage:
        del min_rows, allow_no_data
        self._wait_for_control_enabled(tab_key)
        return self

    def verify_performance_step(
        self,
        *,
        check_label: str,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
    ) -> int:
        del min_rows, allow_no_data
        normalized_url = self.current_url.lower().replace("_", "-")
        assert self.page_hash in normalized_url, (
            f"{check_label} URL hash '{self.page_hash}' not found after navigation"
        )
        label = self._control_label(tab_key)
        assert self.is_control_enabled(tab_key), (
            f"{check_label}: '{label}' control must be visible and enabled"
        )
        record_step_log(
            f"[PERF VERIFY] {check_label}: url OK, '{label}' control enabled"
        )
        return 0
