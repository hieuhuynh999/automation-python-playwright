from __future__ import annotations

from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EtmsLoginBasePage(BasePage):
    """Shared eTMS login form actions (credentials + Select branch button)."""

    _branch_display_hints: dict[str, tuple[str, ...]] = {
        "VNHCM": ("VNHCM", "Hồ Chí Minh", "Ho Chi Minh"),
        "VNHAN": ("VNHAN", "Hà Nội", "Ha Noi"),
    }

    username_selectors = [
        "input[formcontrolname='username']",
        "input[name='username']",
        "input[name='userName']",
        "input[id='username']",
        "input[autocomplete='username']",
        "input[placeholder*='Username']",
        "input[type='email']",
        "input[type='text']",
    ]
    password_selectors = [
        "input[formcontrolname='password']",
        "input[name='password']",
        "input[id='password']",
        "input[autocomplete='current-password']",
        "input[placeholder*='Password']",
        "input[type='password']",
    ]
    login_button_selectors = [
        "button.btn-ftl-primary:has-text('Login')",
        "button[type='submit']:has-text('Login')",
        "button:has-text('Login')",
    ]
    branch_select_button_selectors = [
        "button.btn-ftl-primary:has-text('Select')",
        "button:has-text('Select')",
    ]

    @log_method("Enter username")
    def enter_username(self, username: str) -> EtmsLoginBasePage:
        self.wait_for_visible(
            self.username_selectors,
            "eTMS username input",
        ).fill(username)
        return self

    @log_method("Enter password")
    def enter_password(self, password: str) -> EtmsLoginBasePage:
        self.wait_for_visible(
            self.password_selectors,
            "eTMS password input",
        ).fill(password)
        return self

    @log_method("Click login button")
    def click_login(self) -> EtmsLoginBasePage:
        self.wait_for_visible(
            self.login_button_selectors,
            "eTMS login button",
        ).click()
        self.wait_for_page_stable()
        return self

    @log_method("Login to eTMS")
    def login(self, username: str, password: str) -> EtmsLoginBasePage:
        return self.enter_username(username).enter_password(password).click_login()

    @log_method("Click Select branch button")
    def click_select_branch(
        self,
        expected_url_contains: str = "app/default/home",
    ) -> EtmsLoginBasePage:
        self.wait_for_visible(
            self.branch_select_button_selectors,
            "eTMS Select branch button",
        ).click()
        self.page.wait_for_url(
            f"**/{expected_url_contains}**",
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    @log_method("Check eTMS password field visible")
    def is_password_field_visible(self) -> bool:
        return self.find_visible(self.password_selectors) is not None
