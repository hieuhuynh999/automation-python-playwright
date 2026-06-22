from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage
from automation.pages.efms.efms_navigate_verify_mixin import EfmsNavigateVerifyMixin


class EfmsServicesMenuPage(EfmsNavigateVerifyMixin, BasePage):
    services_menu_selectors = [
        "xpath=//a[contains(@class,'m-menu__toggle') and .//span[normalize-space()='Services']]",
        "xpath=//span[normalize-space()='Services']/ancestor::a[contains(@class,'m-menu__toggle')][1]",
        "xpath=//span[normalize-space()='Services']",
    ]

    services_submenu_selectors = [
        "xpath=//li[contains(@class,'m-menu__item--open')]//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'documentation/')]",
        "xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'documentation/')]",
    ]

    @log_method("Wait for Services sidebar ready")
    def wait_for_services_sidebar_ready(self) -> "EfmsServicesMenuPage":
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.services_menu_selectors,
            "Services menu",
        )
        return self

    @log_method("Open Services Menu")
    def open_services_menu(self) -> "EfmsServicesMenuPage":
        self.wait_for_services_sidebar_ready()
        if self.find_visible(self.services_submenu_selectors) is None:
            toggle = self.wait_for_visible(
                self.services_menu_selectors,
                "Services menu toggle",
            )
            toggle.scroll_into_view_if_needed()
            toggle.click(force=True)
            self.wait_for_page_stable()
        self.wait_for_visible(
            self.services_submenu_selectors,
            "Services submenu",
        )
        self.wait_for_page_stable()
        return self

    def _click_services_submenu(
        self,
        menu_selectors: list[str],
        hash_fragment: str,
    ) -> None:
        self.open_services_menu()

        menu = self.wait_for_visible(menu_selectors, "Services submenu item")
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

    def _is_services_page_displayed(
        self,
        hash_fragment: str,
        title_selectors: list[str],
        title_name: str,
        shipment_item_selectors: list[str] | None = None,
        shipment_item_name: str = "Shipment list",
        min_shipment_items: int = 1,
    ) -> bool:
        if shipment_item_selectors:
            return self._verify_shipment_page_displayed(
                hash_fragment,
                title_selectors,
                title_name,
                shipment_item_selectors,
                shipment_item_name,
                min_shipment_items=min_shipment_items,
            )

        self.wait_for_visible(
            title_selectors,
            title_name,
            timeout=settings.page_load_timeout,
        )
        return hash_fragment in self.current_url
