from automation.config import settings
from automation.logging import log_method
from automation.pages.common.ng_select_component import NgSelectComponent
from automation.pages.etms.etms_login_base_page import EtmsLoginBasePage
from automation.utils.text_utils import text_contains_any


class EtmsLoginPage(EtmsLoginBasePage):
    """Staging eTMS login — branch picker via ng-select."""

    branch_hub_selectors = [
        "ng-select",
        ".select-workplace ng-select",
    ]

    @property
    def _branch_select(self) -> NgSelectComponent:
        return NgSelectComponent(
            self,
            self.branch_hub_selectors,
            "eTMS Branch/Hub dropdown",
        )

    @log_method("Open eTMS login page")
    def open(self) -> EtmsLoginPage:
        self.open_url(settings.etms_base_url)
        return self

    @log_method("Verify Branch/Hub selection page is displayed")
    def is_branch_hub_selection_displayed(self) -> bool:
        if self.is_password_field_visible():
            return False
        return self._branch_select.is_visible()

    @log_method("Select branch")
    def select_branch(self, branch_code: str) -> EtmsLoginPage:
        hints = self._branch_display_hints.get(branch_code.upper(), (branch_code,))
        last_error: Exception | None = None
        for hint in hints:
            try:
                self._branch_select.select_option_by_text(hint)
                return self
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        return self

    @log_method("Get selected branch text")
    def get_selected_branch_text(self) -> str:
        return self._branch_select.get_selected_text()

    @log_method("Check branch selected")
    def is_branch_selected(self, branch_code: str) -> bool:
        hints = self._branch_display_hints.get(branch_code.upper(), (branch_code,))
        return text_contains_any(self.get_selected_branch_text(), hints)
