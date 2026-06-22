from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage
from automation.pages.efms.efms_navigate_verify_mixin import EfmsNavigateVerifyMixin


class EfmsLogisticsMenuPage(EfmsNavigateVerifyMixin, BasePage):
    logistics_menu_selectors = [
        "xpath=//a[contains(@class,'m-menu__toggle') and .//span[normalize-space()='Logistics']]",
        "xpath=//span[normalize-space()='Logistics']/ancestor::a[contains(@class,'m-menu__toggle')][1]",
        "xpath=//span[normalize-space()='Logistics']",
    ]

    logistics_submenu_selectors = [
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'operation/')]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'operation/')]",
    ]

    @log_method("Wait for Logistics sidebar ready")
    def wait_for_logistics_sidebar_ready(self) -> "EfmsLogisticsMenuPage":
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.logistics_menu_selectors,
            "Logistics menu",
        )
        return self

    @log_method("Open Logistics Menu")
    def open_logistics_menu(self) -> "EfmsLogisticsMenuPage":
        self.wait_for_logistics_sidebar_ready()
        if self.find_visible(self.logistics_submenu_selectors) is None:
            toggle = self.wait_for_visible(
                self.logistics_menu_selectors,
                "Logistics menu toggle",
            )
            toggle.scroll_into_view_if_needed()
            toggle.click(force=True)
            self.wait_for_page_stable()
        self.wait_for_visible(
            self.logistics_submenu_selectors,
            "Logistics submenu",
        )
        self.wait_for_page_stable()
        return self

    def _click_logistics_submenu(
        self,
        menu_selectors: list[str],
        hash_fragment: str,
    ) -> None:
        self.open_logistics_menu()

        menu = self.wait_for_visible(menu_selectors, "Logistics submenu item")
        if menu.evaluate("el => el.tagName") == "A":
            target = menu
        else:
            target = menu.locator("xpath=ancestor::a[1]")
        target.scroll_into_view_if_needed()
        self.wait_for_page_stable()
        target.click(force=True)

        self.page.wait_for_url(
            lambda url: hash_fragment in url,
            timeout=settings.page_load_timeout,
        )
        self.wait_for_page_stable()

    def _is_page_displayed(
        self,
        hash_fragment: str,
        title_selectors: list[str],
        table_selectors: list[str],
        title_name: str,
        table_name: str,
        column_headers: list[str],
        min_rows: int = 1,
    ) -> bool:
        return self._verify_list_page_displayed(
            hash_fragment,
            title_selectors,
            table_selectors,
            title_name,
            table_name,
            column_headers,
            min_rows=min_rows,
        )
