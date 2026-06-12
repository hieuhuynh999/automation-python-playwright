from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EfmsHomePage(BasePage):
    username_selectors = [
        "input[name='username']", "input[name='userName']", "input[id='username']",
        "input[id='userName']", "input[autocomplete='username']", "input[placeholder*='Username']",
        "input[placeholder*='User']", "input[type='email']", "input[type='text']",
    ]
    password_selectors = [
        "input[name='password']", "input[id='password']", "input[autocomplete='current-password']",
        "input[placeholder*='Password']", "input[type='password']",
    ]
    submit_selectors = [
        "button[type='submit']", "input[type='submit']", "button:has-text('Login')",
        "button:has-text('Log in')", "button:has-text('Sign in')",
    ]

    company_selectors = [
        "select[formcontrolname='companyId']",
        "select[name='company']",
    ]

    home_title_selectors = [
        "xpath=//h3[normalize-space()='eFMS']",
        "text=eFMS",
    ]

    @log_method("Open eFMS home page")
    def open(self) -> "EfmsHomePage":
        self.open_url(settings.efms_base_url)
        return self

    @log_method("Select company")
    def select_company(self, company: str) -> "EfmsHomePage":
        self.wait_for_visible(
            self.company_selectors,
            "Company dropdown"
        ).select_option(label=company)
        return self

    @log_method("Login to eFMS")
    def login(self, username: str, password: str, company: str) -> "EfmsHomePage":
        self.wait_for_visible(self.username_selectors,
                              "eFMS username input").fill(username)
        self.wait_for_visible(self.password_selectors,
                              "eFMS password input").fill(password)
        self.select_company(company)
        self.wait_for_visible(self.submit_selectors,
                              "eFMS login button").click()
        self.wait_for_dom_content_loaded()
        return self

    @log_method("Verify eFMS title")
    def verify_logo_title(
        self,
        expected_title: str
    ) -> bool:

        actual_title = (
            self.wait_for_visible(
                self.home_title_selectors,
                "eFMS logo title"
            )
            .inner_text()
            .strip()
            
        )

        return actual_title == expected_title
