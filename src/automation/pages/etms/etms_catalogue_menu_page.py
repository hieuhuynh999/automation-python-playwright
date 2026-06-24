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

    catalogue_expanded_selectors = [
        "#catTransportNetwork > a.nav-link",
        "#catPartners > a.nav-link",
        (
            "xpath=//li[@id='cat']//ul[contains(@class,'menu-content')]"
            "//a[contains(@class,'nav-link')]"
        ),
    ]

    transport_network_toggle_selectors = [
        "#catTransportNetwork > a.nav-link",
        (
            "xpath=//li[@id='catTransportNetwork']"
            "//span[normalize-space()='Transport Network']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
    ]

    transport_network_submenu_selectors = [
        "#catOtherPlace > a.nav-link",
        (
            "xpath=//li[@id='catTransportNetwork']"
            "//li[@id='catOtherPlace']//a[contains(@class,'nav-link')]"
        ),
    ]

    partner_toggle_selectors = [
        "#catPartners > a.nav-link",
        (
            "xpath=//li[@id='catPartners']"
            "//span[normalize-space()='Partner']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
    ]

    partner_submenu_selectors = [
        "#catPartnerGroup > a.nav-link",
        (
            "xpath=//li[@id='catPartners']"
            "//li[@id='catPartnerGroup']//a[contains(@class,'nav-link')]"
        ),
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

    def _open_sidebar_submenu(
        self,
        *,
        toggle_selectors: list[str],
        submenu_selectors: list[str],
        toggle_label: str,
        ready_label: str,
    ) -> "EtmsCatalogueMenuPage":
        """Expand a sidebar section when its leaf submenu is not yet visible."""
        if not self._is_menu_item_visible(submenu_selectors):
            self._click_sidebar_link(toggle_selectors, toggle_label)
        self.wait_for_visible(submenu_selectors, ready_label)
        return self

    @log_method("Open Catalogue menu")
    def open_catalogue_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.catalogue_menu_selectors,
            submenu_selectors=self.catalogue_expanded_selectors,
            toggle_label="Catalogue menu",
            ready_label="Catalogue submenu",
        )

    @log_method("Open Transport Network menu")
    def open_transport_network_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.transport_network_toggle_selectors,
            submenu_selectors=self.transport_network_submenu_selectors,
            toggle_label="Transport Network menu",
            ready_label="Places menu under Transport Network",
        )

    @log_method("Open Partner menu")
    def open_partner_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.partner_toggle_selectors,
            submenu_selectors=self.partner_submenu_selectors,
            toggle_label="Partner menu",
            ready_label="Partner Group menu under Partner",
        )
