from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EfmsLoginPage(BasePage):
    username_selectors = [
        "input[name='username']",
        "input[name='userName']",
        "input[id='username']",
        "input[id='userName']",
        "input[autocomplete='username']",
        "input[placeholder*='Username']",
        "input[placeholder*='User']",
        "input[type='email']",
        "input[type='text']",
    ]
    password_selectors = [
        "input[name='password']",
        "input[id='password']",
        "input[autocomplete='current-password']",
        "input[placeholder*='Password']",
        "input[type='password']",
    ]
    submit_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Login')",
        "button:has-text('Log in')",
        "button:has-text('Sign in')",
    ]
    company_selectors = [
        "select[formcontrolname='companyId']",
        "select[name='company']",
    ]

    @log_method("Open eFMS login page")
    def open(self) -> "EfmsLoginPage":
        self.open_url(settings.efms_base_url)
        return self

    @log_method("Enter username")
    def enter_username(self, username: str) -> "EfmsLoginPage":
        self.wait_for_visible(
            self.username_selectors,
            "eFMS username input",
        ).fill(username)
        return self

    @log_method("Enter password")
    def enter_password(self, password: str) -> "EfmsLoginPage":
        self.wait_for_visible(
            self.password_selectors,
            "eFMS password input",
        ).fill(password)
        return self

    @log_method("Select company")
    def select_company(self, company: str) -> "EfmsLoginPage":
        self.wait_for_visible(
            self.company_selectors,
            "Company dropdown",
        ).select_option(label=company)
        return self

    @log_method("Click login button")
    def click_login(self) -> "EfmsLoginPage":
        self.wait_for_visible(
            self.submit_selectors,
            "eFMS login button",
        ).click()
        self.page.wait_for_url(
            lambda url: "#/home" in url and "#/login" not in url,
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    @log_method("Login to eFMS")
    def login(self, username: str, password: str, company: str) -> "EfmsLoginPage":
        return (
            self.enter_username(username)
            .enter_password(password)
            .select_company(company)
            .click_login()
        )

    @log_method("Verify login page is displayed")
    def is_login_page_displayed(self) -> bool:
        self.wait_for_visible(
            self.username_selectors,
            "eFMS username input",
        )
        self.wait_for_visible(
            self.password_selectors,
            "eFMS password input",
        )
        return "#/login" in self.current_url
