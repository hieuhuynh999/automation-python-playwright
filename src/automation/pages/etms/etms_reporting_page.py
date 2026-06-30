from __future__ import annotations

from automation.pages.etms.etms_download_control_page import EtmsDownloadControlPage


class EtmsReportingPage(EtmsDownloadControlPage):
    """VFC top-level Reporting — page load until Download control is visible and enabled."""

    page_key = "reporting"
    page_hash = "accounting/report"
    title = "Reporting"
    sidebar_menu_labels = ("Reporting",)
    performance_menu_suite: str = "reporting"

    def _download_control_selectors(self) -> list[str]:
        return [
            "xpath=//span[normalize-space()='Download']",
            (
                "xpath=//span[normalize-space()='Download']"
                "/ancestor::*[self::button or self::a][1]"
                "[not(@disabled) and not(contains(@class,'disabled'))]"
            ),
            *super()._download_control_selectors(),
        ]
