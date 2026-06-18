from __future__ import annotations

from automation.pages.base_page import BasePage


class BaseComponent:
    """Shared UI widget — compose inside Page Objects, not registered in PageManager."""

    def __init__(self, owner: BasePage, element_name: str) -> None:
        self._owner = owner
        self.element_name = element_name

    @property
    def owner(self) -> BasePage:
        return self._owner

    @property
    def page(self):
        return self._owner.page
