from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EtmsCatalogueMenuPage(BasePage):
    """Sidebar navigation — Catalogue menu group (eTMS nav-link sidebar)."""

    sidebar_ready_selectors = [
        "#cat > a.nav-link",
        "xpath=//li[@id='cat']//span[normalize-space()='Catalogue']",
        ".ftl-main-header",
        "app-home",
    ]

    catalogue_menu_selectors = [
        "#cat > a.nav-link",
        "xpath=//li[@id='cat']//span[normalize-space()='Catalogue']/ancestor::a[contains(@class,'nav-link')][1]",
    ]

    catalogue_submenu_selectors = [
        "#catTransportNetwork > a.nav-link",
        "xpath=//li[@id='cat']//li[@id='catTransportNetwork']//a[contains(@class,'nav-link')]",
    ]

    transport_network_toggle_selectors = [
        "#catTransportNetwork > a.nav-link",
        "xpath=//li[@id='catTransportNetwork']//span[normalize-space()='Transport Network']/ancestor::a[contains(@class,'nav-link')][1]",
    ]

    transport_network_submenu_selectors = [
        "#catOtherPlace > a.nav-link",
        "xpath=//li[@id='catTransportNetwork']//li[@id='catOtherPlace']//a[contains(@class,'nav-link')]",
    ]

    @log_method("Wait for eTMS sidebar navigation ready")
    def wait_for_sidebar_ready(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_page_stable()
        self.wait_for_visible(
            self.sidebar_ready_selectors,
            "eTMS sidebar navigation",
        )
        return self

    def _is_menu_item_visible(self, selectors: list[str]) -> bool:
        return self.find_visible(selectors) is not None

    def _click_sidebar_link(self, selectors: list[str], element_name: str) -> None:
        link = self.wait_for_visible(selectors, element_name)
        link.scroll_into_view_if_needed()
        self.wait_for_page_stable()
        link.click(force=True)
        self.wait_for_page_stable()

    @log_method("Open Catalogue menu")
    def open_catalogue_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        if not self._is_menu_item_visible(self.catalogue_submenu_selectors):
            self._click_sidebar_link(
                self.catalogue_menu_selectors,
                "Catalogue menu",
            )

        self.wait_for_visible(
            self.catalogue_submenu_selectors,
            "Transport Network menu under Catalogue",
        )
        return self

    @log_method("Open Transport Network menu")
    def open_transport_network_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        if not self._is_menu_item_visible(self.transport_network_submenu_selectors):
            self._click_sidebar_link(
                self.transport_network_toggle_selectors,
                "Transport Network menu",
            )

        self.wait_for_visible(
            self.transport_network_submenu_selectors,
            "Places menu under Transport Network",
        )
        return self
