from automation.logging import log_method
from automation.pages.efms.logistics.logistics_menu_page import EfmsLogisticsMenuPage


class EfmsJobManagementPage(EfmsLogisticsMenuPage):
    menu_selectors = [
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'operation/job-management')]",
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='Job Management']]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='Job Management']",
        "xpath=//span[normalize-space()='Job Management']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Job Management']",
        "h3:has-text('Job Management')",
    ]

    list_table_selectors = [
        "xpath=//th[normalize-space()='Job ID']",
        "th:has-text('Job ID')",
    ]

    @log_method("Click Job Management Menu")
    def click_job_management_menu(self) -> "EfmsJobManagementPage":
        self._click_logistics_submenu(
            self.menu_selectors,
            "/home/operation/job-management",
        )
        return self

    @log_method("Verify Job Management is displayed")
    def is_job_management_displayed(self) -> bool:
        return self._is_page_displayed(
            "#/home/operation/job-management",
            self.list_title_selectors,
            self.list_table_selectors,
            "Job Management title",
            "Job Management table",
        )
