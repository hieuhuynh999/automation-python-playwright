from __future__ import annotations

from automation.logging import log_method
from automation.pages.base_page import BasePage
from automation.pages.common.base_component import BaseComponent


class NativeSelectComponent(BaseComponent):
    """HTML <select> dropdown — eFMS company picker."""

    def __init__(
        self,
        owner: BasePage,
        select_selectors: list[str],
        element_name: str,
    ) -> None:
        super().__init__(owner, element_name)
        self.select_selectors = select_selectors

    @log_method("Select native dropdown option by label")
    def select_by_label(self, label: str) -> None:
        self._owner.wait_for_visible(
            self.select_selectors,
            self.element_name,
        ).select_option(label=label)

    def is_visible(self) -> bool:
        return self._owner.find_visible(self.select_selectors) is not None
