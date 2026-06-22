from automation.logging import log_method
from automation.pages.efms.logistics.logistics_menu_page import EfmsLogisticsMenuPage


class EfmsCustomClearancePage(EfmsLogisticsMenuPage):
    menu_selectors = [
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'operation/custom-clearance')]",
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='Customs Clearance']]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='Customs Clearance']",
        "xpath=//span[normalize-space()='Customs Clearance']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Customs Clearance']",
        "h3:has-text('Customs Clearance')",
    ]

    list_table_selectors = [
        "xpath=//th[normalize-space()='Clearance Date']",
        "th:has-text('Clearance Date')",
        "xpath=//th[normalize-space()='Custom No']",
    ]

    list_column_headers = [
        "Clearance Date",
    ]

    @log_method("Click Customs Clearance Menu")
    def click_custom_clearance_menu(self) -> "EfmsCustomClearancePage":
        self._click_logistics_submenu(
            self.menu_selectors,
            "/home/operation/custom-clearance",
        )
        return self

    @log_method("Verify Customs Clearance is displayed")
    def is_custom_clearance_displayed(self) -> bool:
        return self._is_page_displayed(
            "#/home/operation/custom-clearance",
            self.list_title_selectors,
            self.list_table_selectors,
            "Customs Clearance title",
            "Customs Clearance table",
            self.list_column_headers,
        )
