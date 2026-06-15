from automation.logging import log_method
from automation.pages.efms.commercial.commercial_menu_page import EfmsCommercialMenuPage


class EfmsWorkOrderPage(EfmsCommercialMenuPage):
    menu_selectors = [
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'commercial/work-order')]",
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='Work Order']]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='Work Order']",
        "xpath=//span[normalize-space()='Work Order']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Work Order']",
        "h3:has-text('Work Order')",
    ]

    list_table_selectors = [
        "xpath=//th[normalize-space()='Work Order No.']",
        "th:has-text('Work Order No.')",
    ]

    @log_method("Click Work Order Menu")
    def click_work_order_menu(self) -> "EfmsWorkOrderPage":
        self._click_commercial_submenu(
            self.menu_selectors,
            "/home/commercial/work-order",
        )
        return self

    @log_method("Verify Work Order List is displayed")
    def is_work_order_list_displayed(self) -> bool:
        return self._is_page_displayed(
            "#/home/commercial/work-order",
            self.list_title_selectors,
            self.list_table_selectors,
            "Work Order list title",
            "Work Order list table",
        )
