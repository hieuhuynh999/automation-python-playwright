from automation.logging import log_method
from automation.pages.efms.commercial.commercial_menu_page import EfmsCommercialMenuPage


class EfmsCustomerPage(EfmsCommercialMenuPage):
    menu_selectors = [
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'commercial/customer')]",
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='Customer']]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='Customer']",
        "xpath=//span[normalize-space()='Customer']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Customer']",
        "h3:has-text('Customer')",
    ]

    list_table_selectors = [
        "xpath=//th[normalize-space()='Partner ID']",
        "th:has-text('Partner ID')",
    ]

    list_column_headers = [
        "Partner ID",
        "Name ABBR",
    ]

    @log_method("Click Customer Menu")
    def click_customer_menu(self) -> "EfmsCustomerPage":
        self._click_commercial_submenu(
            self.menu_selectors,
            "/home/commercial/customer",
        )
        return self

    @log_method("Verify Customer List is displayed")
    def is_customer_list_displayed(self) -> bool:
        return self._is_page_displayed(
            "#/home/commercial/customer",
            self.list_title_selectors,
            self.list_table_selectors,
            "Customer list title",
            "Customer list table",
            self.list_column_headers,
        )
