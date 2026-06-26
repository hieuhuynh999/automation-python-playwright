from __future__ import annotations

import time

from automation.config import settings
from automation.logging import log_method
from automation.logging.step_logger import record_step_log
from automation.pages.etms.etms_catalogue_menu_page import (
    EtmsCatalogueMenuPage,
    _catalogue_submenu_link_by_label,
    _sidebar_link_by_href,
    etms_page_title_selectors,
)


class EtmsQuotationFormPage(EtmsCatalogueMenuPage):
    """Quotation create form — sidebar page load until Search control is visible and enabled."""

    page_key: str
    page_hash: str
    title: str
    sidebar_menu_labels: tuple[str, ...]
    ready_control_label: str = "Search"

    loading_overlay_selectors = [
        ".m-blockui",
        ".block-ui-wrapper.block-ui-active",
        "xpath=//div[contains(@class,'block-ui') and contains(@class,'active')]",
        ".ng-progress-bar[active='true']",
    ]

    def _menu_selectors(self) -> list[str]:
        labels = self.sidebar_menu_labels
        selectors: list[str] = []
        for label in labels:
            selectors.extend(
                [
                    _catalogue_submenu_link_by_label(label),
                    (
                        "xpath=//a[contains(@class,'nav-link')]"
                        f"[.//span[normalize-space()='{label}']]"
                    ),
                ]
            )
        selectors.append(_sidebar_link_by_href(self.page_hash))
        return list(dict.fromkeys(selectors))

    @property
    def page_title_selectors(self) -> list[str]:
        return etms_page_title_selectors(self.title)

    def _search_visible_selectors(self) -> list[str]:
        label = self.ready_control_label
        return [
            f"xpath=//span[normalize-space()='{label}']",
            (
                f"xpath=//button["
                f"normalize-space()='{label}' or .//span[normalize-space()='{label}']]"
            ),
            (
                f"xpath=//a["
                f"normalize-space()='{label}' or .//span[normalize-space()='{label}']]"
            ),
        ]

    def _search_enabled_selectors(self) -> list[str]:
        label = self.ready_control_label
        disabled_clause = " and not(@disabled) and not(contains(@class,'disabled'))"
        return [
            (
                f"xpath=//button["
                f"(normalize-space()='{label}' or .//span[normalize-space()='{label}'])"
                f"{disabled_clause}]"
            ),
            (
                f"xpath=//a["
                f"(normalize-space()='{label}' or .//span[normalize-space()='{label}'])"
                f"{disabled_clause}]"
            ),
            (
                f"xpath=//span[normalize-space()='{label}']"
                "/ancestor::*[self::button or self::a][1]"
                f"[not(@disabled) and not(contains(@class,'disabled'))]"
            ),
        ]

    def is_search_visible(self) -> bool:
        return self.find_visible(self._search_visible_selectors()) is not None

    def is_search_enabled(self) -> bool:
        return self.find_visible(self._search_enabled_selectors()) is not None

    def _wait_for_loading_overlay_hidden(self, timeout: int | None = None) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.find_visible(self.loading_overlay_selectors) is None:
                return
            self.page.wait_for_timeout(settings.polling_interval)

    def _wait_for_search_ready(self, timeout: int | None = None) -> None:
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.is_search_visible() and self.is_search_enabled():
                return
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(
            f"{self.title} Search control not visible and enabled after {timeout}ms. "
            f"URL: {self.current_url}"
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
        self._wait_for_loading_overlay_hidden()
        self.wait_for_page_stable()
        self._wait_for_search_ready()

    def confirm_grid_loaded(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
        allow_no_data: bool = False,
    ) -> EtmsQuotationFormPage:
        del min_rows, tab_key, allow_no_data
        self._wait_for_loading_overlay_hidden()
        self._wait_for_search_ready()
        return self

    def wait_before_next_pricing_navigation(self) -> EtmsQuotationFormPage:
        self._wait_for_loading_overlay_hidden()
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
        assert self.is_search_visible(), (
            f"{check_label}: {self.ready_control_label} button/span must be visible"
        )
        assert self.is_search_enabled(), (
            f"{check_label}: {self.ready_control_label} button/span must be enabled"
        )
        record_step_log(
            f"[PERF VERIFY] {check_label}: url OK, "
            f"{self.ready_control_label} control visible and enabled"
        )
        return 0

    @log_method("Open quotation form page via sidebar menu")
    def open_via_sidebar_menu(self) -> EtmsQuotationFormPage:
        self.open_quotation_menu()
        self._navigate_to_page()
        self._wait_for_search_ready()
        return self


class EtmsCreateFclQuotationPage(EtmsQuotationFormPage):
    """Quotation > Create FCL Quotation."""

    page_key = "create_fcl_quotation"
    page_hash = "quotation/fcl-quotation"
    title = "Create FCL Quotation"
    sidebar_menu_labels = ("Create FCL Quotation",)


class EtmsCreateLclQuotationPage(EtmsQuotationFormPage):
    """Quotation > Create LCL Quotation."""

    page_key = "create_lcl_quotation"
    page_hash = "quotation/lcl-quotation"
    title = "Create LCL Quotation"
    sidebar_menu_labels = ("Create LCL Quotation",)


class EtmsCreateDistributionQuotationPage(EtmsQuotationFormPage):
    """Quotation > Create Distribution Quotation."""

    page_key = "create_distribution_quotation"
    page_hash = "quotation/dtb-create-rate-card"
    title = "Create Distribution Quotation"
    sidebar_menu_labels = ("Create Distribution Quotation",)
