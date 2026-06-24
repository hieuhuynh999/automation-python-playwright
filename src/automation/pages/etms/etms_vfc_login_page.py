from automation.config import settings
from automation.logging import log_method
from automation.pages.etms.etms_login_base_page import EtmsLoginBasePage


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

    @log_method("Open VFC eTMS login page")
    def open(self) -> EtmsVfcLoginPage:
        self.open_url(settings.vfc_etms_base_url)
        return self

    @log_method("Verify Branch/Hub selection page is displayed")
    def is_branch_hub_selection_displayed(self) -> bool:
        if self.is_password_field_visible():
            return False
        return self.find_visible(self.branch_custom_search_input_selectors) is not None

    @log_method("Select branch via ngx-custom-search")
    def select_branch(self, branch_code: str) -> EtmsVfcLoginPage:
        hints = self._branch_display_hints.get(branch_code.upper(), (branch_code,))
        trigger = self.find_visible(self.branch_custom_search_input_selectors)
        if trigger is not None:
            trigger.click()
            self.wait_for_page_stable()

        search = self.wait_for_visible(
            self.branch_custom_search_field_selectors,
            "Branch/Hub search input (txtSearchAll)",
        )
        search.click()
        search.fill("")
        search.fill(branch_code)
        self.wait_for_page_stable()

        search_terms = (branch_code, *hints)
        last_error: Exception | None = None
        for term in dict.fromkeys(search_terms):
            option_selectors = [
                f"xpath=//ng-dropdown-panel//div[contains(@class,'ng-option') and contains(.,'{term}')]",
                f".ng-dropdown-panel .ng-option:has-text('{term}')",
                f"xpath=//*[contains(@class,'ng-option') and contains(.,'{term}')]",
                (
                    "xpath=//ngx-custom-search//div[contains(@class,'ng-option') "
                    f"and contains(.,'{term}')]"
                ),
            ]
            try:
                option = self.wait_for_visible(
                    option_selectors,
                    f"Branch/Hub option: {term}",
                )
                option.click(force=True)
                self.page.locator(".ng-dropdown-panel").wait_for(
                    state="hidden",
                    timeout=settings.browser_timeout,
                )
                self.wait_for_page_stable()
                return self
            except Exception as exc:
                last_error = exc

        if last_error is not None:
            raise last_error
        return self
