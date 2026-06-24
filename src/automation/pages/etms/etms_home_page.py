from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EtmsHomePage(BasePage):
    dashboard_ready_selectors = [
        "app-home",
        "app-main .page-wrapper",
        ".ftl-main-header",
        ".page-header.navbar-fixed-top",
    ]

    @log_method("Verify eTMS dashboard is displayed")
    def is_dashboard_displayed(self) -> bool:
        self.wait_for_visible(
            self.dashboard_ready_selectors,
            "eTMS dashboard",
            timeout=settings.page_load_timeout,
        )
        return True

    @log_method("Check eTMS home URL")
    def is_home_url(self, expected_fragment: str = "app/default/home") -> bool:
        return expected_fragment in self.current_url

    @log_method("Verify eTMS title is displayed on home page")
    def is_etms_title_displayed(self, title: str = "eTMS") -> bool:
        selectors = [
            f"xpath=//*[normalize-space()='{title}']",
            f"xpath=//h1[contains(normalize-space(),'{title}')]",
            f"xpath=//h2[contains(normalize-space(),'{title}')]",
            f"xpath=//h3[contains(normalize-space(),'{title}')]",
            f"xpath=//*[contains(@class,'page-title') and contains(normalize-space(),'{title}')]",
            f"xpath=//*[contains(@class,'navbar-brand') and contains(normalize-space(),'{title}')]",
        ]
        self.wait_for_visible(selectors, f"Home page title: {title}")
        return True
