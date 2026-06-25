import time

from automation.config import settings
from automation.logging import log_method, logger
from automation.pages.etms.etms_login_base_page import EtmsLoginBasePage
from automation.utils.text_utils import text_contains_any


class EtmsVfcLoginPage(EtmsLoginBasePage):
    """VFC eTMS login — branch picker via ngx-custom-search + txtSearchAll."""

    branch_custom_search_input_selectors = [
        (
            "xpath=//label[normalize-space()='Branch/Hub']"
            "/following-sibling::ngx-custom-search//div[@class='ng-input']"
        ),
        (
            "xpath=//label[text()='Branch/Hub']"
            "/following-sibling::ngx-custom-search//div[@class='ng-input']"
        ),
        "#txtSearchAll",
    ]
    branch_custom_search_root_selectors = [
        (
            "xpath=//label[normalize-space()='Branch/Hub']"
            "/following-sibling::ngx-custom-search"
        ),
        (
            "xpath=//label[text()='Branch/Hub']"
            "/following-sibling::ngx-custom-search"
        ),
    ]
    branch_custom_search_field_selectors = [
        "#txtSearchAll",
        "input#txtSearchAll",
        "xpath=//input[@id='txtSearchAll']",
        (
            "xpath=//label[normalize-space()='Branch/Hub']"
            "/following-sibling::ngx-custom-search//input[@id='txtSearchAll']"
        ),
        (
            "xpath=//label[text()='Branch/Hub']"
            "/following-sibling::ngx-custom-search//input[@id='txtSearchAll']"
        ),
        "ngx-custom-search input[type='text']",
    ]
    branch_selected_value_selectors = [
        (
            "xpath=//label[normalize-space()='Branch/Hub']"
            "/following-sibling::ngx-custom-search//span[contains(@class,'ng-value-label')]"
        ),
        (
            "xpath=//label[normalize-space()='Branch/Hub']"
            "/following-sibling::ngx-custom-search//div[contains(@class,'ng-select-container')]"
        ),
        "ngx-custom-search .ng-value-label",
        "ngx-custom-search .ng-value",
        "ngx-custom-search .ng-select-container",
    ]

    dropdown_panel_selector = ".ng-dropdown-panel"

    @log_method("Open VFC eTMS login page")
    def open(self) -> EtmsVfcLoginPage:
        self.open_url(settings.vfc_etms_base_url)
        return self

    @log_method("Login to VFC eTMS")
    def login(self, username: str, password: str) -> EtmsVfcLoginPage:
        super().login(username, password)
        self.wait_for_branch_hub_selection_displayed()
        return self

    @log_method("Verify Branch/Hub selection page is displayed")
    def is_branch_hub_selection_displayed(self) -> bool:
        if self.is_password_field_visible():
            return False
        return self.find_visible(self.branch_custom_search_input_selectors) is not None

    @log_method("Wait for Branch/Hub selection page")
    def wait_for_branch_hub_selection_displayed(
        self,
        timeout: int | None = None,
    ) -> EtmsVfcLoginPage:
        """Poll until login form is gone and Branch/Hub picker is ready."""
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000

        while time.monotonic() < deadline:
            if not self.is_password_field_visible():
                if self.find_visible(self.branch_custom_search_input_selectors) is not None:
                    logger.info("VFC Branch/Hub selection page is displayed")
                    return self
            self.page.wait_for_timeout(settings.polling_interval)

        raise AssertionError(
            self._build_wait_error(
                "VFC Branch/Hub selection page",
                self.branch_custom_search_input_selectors,
                timeout,
            )
        )

    @log_method("Select branch via ngx-custom-search")
    def select_branch(self, branch_code: str) -> EtmsVfcLoginPage:
        hints = self._branch_display_hints.get(branch_code.upper(), (branch_code,))
        trigger = self.wait_for_visible(
            self.branch_custom_search_input_selectors,
            "Branch/Hub dropdown trigger",
            timeout=settings.component_interaction_timeout,
        )
        trigger.click()
        self.page.locator(self.dropdown_panel_selector).wait_for(
            state="visible",
            timeout=settings.component_interaction_timeout,
        )
        self.wait_for_page_stable()

        search = self.wait_for_visible(
            self.branch_custom_search_field_selectors,
            "Branch/Hub search input (txtSearchAll)",
            timeout=settings.component_interaction_timeout,
        )
        search.click()
        search.fill("")
        search.fill(branch_code)
        self.wait_for_page_stable()

        panel = self.page.locator(self.dropdown_panel_selector)
        search_terms = (branch_code, *hints)
        last_error: Exception | None = None
        for term in dict.fromkeys(search_terms):
            option = panel.locator(".ng-option").filter(has_text=term).first
            try:
                option.wait_for(
                    state="visible",
                    timeout=settings.browser_timeout,
                )
                option.scroll_into_view_if_needed()
                option.click()
                panel.wait_for(
                    state="hidden",
                    timeout=settings.component_interaction_timeout,
                )
                self.wait_for_page_stable()
                return self
            except Exception as exc:
                last_error = exc

        if last_error is not None:
            raise last_error
        return self

    @log_method("Get selected branch text")
    def get_selected_branch_text(self) -> str:
        value = self.find_visible(self.branch_selected_value_selectors)
        if value is not None:
            text = value.inner_text().strip()
            if text:
                return text

        search = self.find_visible(self.branch_custom_search_field_selectors)
        if search is not None:
            try:
                value = search.input_value().strip()
                if value:
                    return value
            except Exception:
                pass

        return ""

    @log_method("Check branch selected")
    def is_branch_selected(self, branch_code: str) -> bool:
        hints = self._branch_display_hints.get(branch_code.upper(), (branch_code,))
        return text_contains_any(self.get_selected_branch_text(), hints)

    @log_method("Wait for branch selected")
    def wait_for_branch_selected(
        self,
        branch_code: str,
        timeout: int | None = None,
    ) -> EtmsVfcLoginPage:
        timeout = timeout or settings.component_interaction_timeout
        hints = self._branch_display_hints.get(branch_code.upper(), (branch_code,))
        deadline = time.monotonic() + timeout / 1000

        while time.monotonic() < deadline:
            if self.is_branch_selected(branch_code):
                return self
            self.page.wait_for_timeout(settings.polling_interval)

        selected_text = self.get_selected_branch_text()
        raise AssertionError(
            f"Branch '{branch_code}' not selected after {timeout}ms. "
            f"Visible text: {selected_text!r}. Expected one of: {hints}"
        )
