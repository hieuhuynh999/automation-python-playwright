from __future__ import annotations

from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage
from automation.pages.common.base_component import BaseComponent


class NgSelectComponent(BaseComponent):
    """Angular ng-select dropdown — eTMS branch picker, eFMS form fields."""

    dropdown_panel_selector = ".ng-dropdown-panel"
    option_selector = ".ng-option"

    def __init__(
        self,
        owner: BasePage,
        root_selectors: list[str],
        element_name: str,
    ) -> None:
        super().__init__(owner, element_name)
        self.root_selectors = root_selectors

    @log_method("Open ng-select")
    def open(self) -> None:
        self._owner.wait_for_visible(self.root_selectors, self.element_name).click()
        self.page.locator(self.dropdown_panel_selector).wait_for(
            state="visible",
            timeout=settings.browser_timeout,
        )

    @log_method("Select ng-select option by text")
    def select_option_by_text(self, option_text: str) -> None:
        self.open()
        option = (
            self.page.locator(self.dropdown_panel_selector)
            .locator(self.option_selector)
            .filter(has_text=option_text)
            .first
        )
        option.wait_for(state="visible", timeout=settings.browser_timeout)
        option.click()
        self.page.locator(self.dropdown_panel_selector).wait_for(
            state="hidden",
            timeout=settings.browser_timeout,
        )
        self._owner.wait_for_page_stable()

    @log_method("Get ng-select selected text")
    def get_selected_text(self) -> str:
        root = self._owner.wait_for_visible(self.root_selectors, self.element_name)
        container = root.locator(".ng-select-container").first
        if container.count() and container.is_visible():
            return container.inner_text().strip()
        return root.inner_text().strip()

    def is_visible(self) -> bool:
        return self._owner.find_visible(self.root_selectors) is not None
