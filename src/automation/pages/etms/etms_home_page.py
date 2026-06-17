from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EtmsHomePage(BasePage):
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

    @log_method("Open eTMS home page")
    def open(self) -> "EtmsHomePage":
        self.open_url(settings.etms_base_url)
        return self

    @log_method("Login to eTMS")
    def login(self, username: str, password: str) -> "EtmsHomePage":
        self.wait_for_visible(self.username_selectors, "eTMS username input").fill(username)
        self.wait_for_visible(self.password_selectors, "eTMS password input").fill(password)
        self.wait_for_visible(self.submit_selectors, "eTMS login button").click()
        self.wait_for_dom_content_loaded()
        return self

    @log_method("Check eTMS password field visible")
    def is_password_field_visible(self) -> bool:
        return self.find_visible(self.password_selectors) is not None
