from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EfmsHomePage(BasePage):
    dashboard_ready_selectors = [
        "xpath=//a[contains(@class,'m-menu__toggle') and .//span[normalize-space()='Commercial']]",
        "xpath=//span[normalize-space()='Commercial']/ancestor::a[contains(@class,'m-menu__toggle')][1]",
        "xpath=//span[normalize-space()='Commercial']",
        "xpath=//span[normalize-space()='Dashboard']",
    ]

    user_menu_selectors = [
        "[aria-label='User menu']",
        "xpath=//li[contains(@class,'m-topbar__user-profile')]//a[contains(@class,'m-dropdown__toggle')]",
        ".m-topbar__user-profile .m-nav__link.m-dropdown__toggle",
        ".m-topbar__user-profile a.m-nav__link",
        "[class*='m-topbar__user-profile'] a[class*='dropdown-toggle']",
    ]

    logout_selectors = [
        "[aria-label='Sign Out']",
        "[aria-label='Logout']",
        "xpath=//li[contains(@class,'m-topbar__user-profile')]//span[normalize-space()='Sign Out']",
        "xpath=//li[contains(@class,'m-topbar__user-profile')]//a[contains(@class,'m-dropdown__item') and contains(.,'Sign Out')]",
        "span:has-text('Sign Out')",
        "a:has-text('Sign Out')",
        "button:has-text('Sign Out')",
        "span:has-text('Logout')",
        "a:has-text('Logout')",
    ]

    confirm_yes_selectors = [
        "[data-testid='confirm-yes']",
        "#confirm-yes",
        "button[name='yes']",
        "[aria-label='Yes']",
        "button:has-text('Yes')",
        ".swal2-confirm",
        "xpath=//div[contains(@class,'modal')]//button[normalize-space()='Yes']",
        "xpath=//button[contains(@class,'btn') and normalize-space()='Yes']",
    ]

    @log_method("Verify dashboard is displayed")
    def is_dashboard_displayed(self) -> bool:
        self.wait_for_visible(
            self.dashboard_ready_selectors,
            "eFMS dashboard navigation",
            timeout=settings.page_load_timeout,
        )
        return "#/home" in self.current_url

    @log_method("Wait for dashboard DOM stable")
    def wait_for_dashboard_ready(self) -> "EfmsHomePage":
        self.wait_for_visible(
            self.dashboard_ready_selectors,
            "eFMS dashboard navigation",
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    @log_method("Click user menu")
    def click_user_menu(self) -> "EfmsHomePage":
        self.wait_for_visible(
            self.user_menu_selectors,
            "User menu",
        ).click()
        return self

    @log_method("Click sign out")
    def click_logout(self) -> "EfmsHomePage":
        self.wait_for_visible(
            self.logout_selectors,
            "Sign Out button",
        ).click()
        return self

    @log_method('Click "Yes" confirm button')
    def click_confirm_yes(self) -> "EfmsHomePage":
        self.wait_for_visible(
            self.confirm_yes_selectors,
            "Yes confirm button",
        ).click()
        self.page.wait_for_url(
            lambda url: "#/login" in url,
            timeout=settings.page_load_timeout,
        )
        self.wait_for_dom_content_loaded()
        return self
