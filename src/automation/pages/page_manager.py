from playwright.sync_api import Page

from automation.pages.efms import EfmsHomePage
from automation.pages.etms import EtmsHomePage


class PageManager:
    def __init__(self, page: Page):
        self.page = page
        self._efms_home_page: EfmsHomePage | None = None
        self._etms_home_page: EtmsHomePage | None = None

    @property
    def efms_home_page(self) -> EfmsHomePage:
        if self._efms_home_page is None:
            self._efms_home_page = EfmsHomePage(self.page)
        return self._efms_home_page

    @property
    def etms_home_page(self) -> EtmsHomePage:
        if self._etms_home_page is None:
            self._etms_home_page = EtmsHomePage(self.page)
        return self._etms_home_page
