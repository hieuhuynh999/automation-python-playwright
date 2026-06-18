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
