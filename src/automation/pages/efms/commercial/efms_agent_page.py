from automation.logging import log_method
from automation.pages.efms.commercial.commercial_menu_page import EfmsCommercialMenuPage


class EfmsAgentPage(EfmsCommercialMenuPage):
    menu_selectors = [
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'commercial/agent')]",
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[.//span[normalize-space()='Agent']]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//span[normalize-space()='Agent']",
        "xpath=//span[normalize-space()='Agent']",
    ]

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Agent']",
        "h3:has-text('Agent')",
    ]

    list_table_selectors = [
        "xpath=//th[normalize-space()='Partner ID']",
        "th:has-text('Partner ID')",
    ]

    @log_method("Click Agent Menu")
    def click_agent_menu(self) -> "EfmsAgentPage":
        self._click_commercial_submenu(
            self.menu_selectors,
            "/home/commercial/agent",
        )
        return self

    @log_method("Verify Agent List is displayed")
    def is_agent_list_displayed(self) -> bool:
        return self._is_page_displayed(
            "#/home/commercial/agent",
            self.list_title_selectors,
            self.list_table_selectors,
            "Agent list title",
            "Agent list table",
        )
