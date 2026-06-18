from __future__ import annotations

from automation.logging import log_method
from automation.pages.base_page import BasePage
from automation.pages.common.base_component import BaseComponent


class SwalModalComponent(BaseComponent):
    """SweetAlert2 popup — eFMS confirm / delete dialogs."""

    popup_selectors = [
        ".swal2-popup",
        "xpath=//div[contains(@class,'swal2-popup')]",
    ]
    confirm_selectors = [
        ".swal2-confirm",
        "button.swal2-confirm",
    ]
    message_selectors = [
        ".swal2-html-container",
        ".swal2-title",
    ]

    @log_method("Wait for SweetAlert popup")
    def wait_for_popup(self) -> None:
        self._owner.wait_for_visible(self.popup_selectors, "SweetAlert popup")

    @log_method("Click SweetAlert confirm")
    def click_confirm(self) -> None:
        self.wait_for_popup()
        self._owner.wait_for_visible(self.confirm_selectors, "SweetAlert confirm button").click()
        self._owner.wait_for_page_stable()

    @log_method("Check SweetAlert message visible")
    def is_message_visible(self, message: str) -> bool:
        selectors = [
            f".swal2-html-container:has-text('{message}')",
            f".swal2-title:has-text('{message}')",
        ]
        return self._owner.find_visible(selectors) is not None

    def is_visible(self) -> bool:
        return self._owner.find_visible(self.popup_selectors) is not None
