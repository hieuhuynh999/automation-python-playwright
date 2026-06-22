from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage
from automation.pages.common.ng_select_component import NgSelectComponent
from automation.utils.text_utils import text_contains_any


class EtmsLoginPage(BasePage):
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
    branch_hub_selectors = [
        "ng-select",
        ".select-workplace ng-select",
    ]
    branch_select_button_selectors = [
        "button.btn-ftl-primary:has-text('Select')",
        "button:has-text('Select')",
    ]

    @property
    def _branch_select(self) -> NgSelectComponent:
        return NgSelectComponent(
            self,
            self.branch_hub_selectors,
            "eTMS Branch/Hub dropdown",
        )

    @log_method("Open eTMS login page")
    def open(self) -> "EtmsLoginPage":
        self.open_url(settings.etms_base_url)
        return self

    @log_method("Enter username")
    def enter_username(self, username: str) -> "EtmsLoginPage":
        self.wait_for_visible(
            self.username_selectors,
            "eTMS username input",
        ).fill(username)
        return self

    @log_method("Enter password")
    def enter_password(self, password: str) -> "EtmsLoginPage":
        self.wait_for_visible(
            self.password_selectors,
            "eTMS password input",
        ).fill(password)
        return self

    @log_method("Click login button")
    def click_login(self) -> "EtmsLoginPage":
        self.wait_for_visible(
            self.login_button_selectors,
            "eTMS login button",
        ).click()
        self.wait_for_page_stable()
        return self

    @log_method("Login to eTMS")
    def login(self, username: str, password: str) -> "EtmsLoginPage":
        return self.enter_username(username).enter_password(password).click_login()

    @log_method("Verify Branch/Hub selection page is displayed")
    def is_branch_hub_selection_displayed(self) -> bool:
        if self.is_password_field_visible():
            return False
        return self._branch_select.is_visible()

    @log_method("Select branch")
    def select_branch(self, branch_code: str) -> "EtmsLoginPage":
        self._branch_select.select_option_by_text(branch_code)
        return self

    @log_method("Click Select branch button")
    def click_select_branch(self) -> "EtmsLoginPage":
        self.wait_for_visible(
            self.branch_select_button_selectors,
            "eTMS Select branch button",
        ).click()
        self.page.wait_for_url(
            "**/app/default/home**",
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()
        return self

    @log_method("Get selected branch text")
    def get_selected_branch_text(self) -> str:
        return self._branch_select.get_selected_text()

    @log_method("Check branch selected")
    def is_branch_selected(self, branch_code: str) -> bool:
        hints = self._branch_display_hints.get(branch_code.upper(), (branch_code,))
        return text_contains_any(self.get_selected_branch_text(), hints)

    @log_method("Check eTMS password field visible")
    def is_password_field_visible(self) -> bool:
        return self.find_visible(self.password_selectors) is not None
