from __future__ import annotations

from automation.logging import log_method
from automation.pages.etms.etms_download_control_page import EtmsDownloadControlPage


class EtmsPricingReportPage(EtmsDownloadControlPage):
    """Pricing Report — sidebar page load until Download control is enabled."""

    page_key = "pricing_report"
    page_hash = "accounting/report"
    title = "Pricing Report"
    sidebar_menu_labels = ("Pricing Report",)
    menu_parent_label: str = "Pricing"
    performance_menu_suite: str = "pricing"

    @log_method("Open Pricing Report via sidebar menu")
    def open_via_sidebar_menu(self) -> EtmsPricingReportPage:
        self.open_pricing_menu()
        self._navigate_to_page()
        self._wait_for_download_enabled()
        return self

    def wait_before_next_pricing_navigation(self) -> EtmsPricingReportPage:
        return self.wait_before_next_catalogue_navigation()
