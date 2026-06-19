from __future__ import annotations

import time

from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage
from automation.pages.common.base_component import BaseComponent

_DEFAULT_POPUP_SELECTORS = [
    ".swal2-popup",
    "xpath=//div[contains(@class,'swal2-popup')]",
]
_DEFAULT_CONFIRM_SELECTORS = [
    ".swal2-confirm",
    "button.swal2-confirm",
]


class SwalModalComponent(BaseComponent):
    """SweetAlert2 popup — eFMS confirm / delete dialogs."""

    def __init__(
        self,
        owner: BasePage,
        element_name: str,
        popup_selectors: list[str] | None = None,
        confirm_selectors: list[str] | None = None,
    ) -> None:
        super().__init__(owner, element_name)
        self.popup_selectors = popup_selectors or list(_DEFAULT_POPUP_SELECTORS)
        self.confirm_selectors = confirm_selectors or list(_DEFAULT_CONFIRM_SELECTORS)

    @log_method("Wait for SweetAlert popup")
    def wait_for_popup(self, timeout: int | None = None) -> None:
        self._owner.wait_for_visible(
            self.popup_selectors,
            self.element_name,
            timeout=timeout,
        )

    @log_method("Click SweetAlert confirm")
    def click_confirm(self, *, force: bool = False) -> None:
        self.wait_for_popup()
        self._owner.wait_for_visible(
            self.confirm_selectors,
            f"{self.element_name} confirm button",
        ).click(force=force)
        self._owner.wait_for_page_stable()

    @log_method("Wait for SweetAlert popup closed")
    def wait_until_closed(self, timeout: int | None = None) -> None:
        timeout = timeout or settings.page_load_timeout
        try:
            self.page.wait_for_function(
                "() => !document.querySelector('.swal2-popup')",
                timeout=timeout,
            )
            return
        except Exception:
            pass

        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if not self.is_visible():
                return
            self.page.wait_for_timeout(settings.polling_interval)

    @log_method("Check SweetAlert message visible")
    def is_message_visible(self, message: str) -> bool:
        selectors = [
            f".swal2-html-container:has-text('{message}')",
            f".swal2-title:has-text('{message}')",
        ]
        return self._owner.find_visible(selectors) is not None

    def is_visible(self) -> bool:
        return self._owner.find_visible(self.popup_selectors) is not None
