from automation.logging import log_method
from automation.pages.efms.logistics.logistics_menu_page import EfmsLogisticsMenuPage


class EfmsTruckingInlandPage(EfmsLogisticsMenuPage):
    menu_selectors = [
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'operation/trucking-inland')]",
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='Trucking Inland']]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='Trucking Inland']",
        "xpath=//span[normalize-space()='Trucking Inland']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Trucking Inland']",
        "h3:has-text('Trucking Inland')",
    ]

    list_table_selectors = [
        "xpath=//th[normalize-space()='Job ID']",
        "th:has-text('Job ID')",
    ]

    @log_method("Click Trucking Inland Menu")
    def click_trucking_inland_menu(self) -> "EfmsTruckingInlandPage":
        self._click_logistics_submenu(
            self.menu_selectors,
            "/home/operation/trucking-inland",
        )
        return self

    @log_method("Verify Trucking Inland is displayed")
    def is_trucking_inland_displayed(self) -> bool:
        return self._is_page_displayed(
            "#/home/operation/trucking-inland",
            self.list_title_selectors,
            self.list_table_selectors,
            "Trucking Inland title",
            "Trucking Inland table",
        )
