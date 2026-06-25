import time

from playwright.sync_api import Locator

from automation.config import settings
from automation.logging import log_method, logger
from automation.pages.base_page import BasePage


def _sidebar_link_by_label(label: str) -> str:
    return (
        "xpath=//a[contains(@class,'nav-link')]"
        f"[.//span[normalize-space()='{label}']]"
    )


def _catalogue_submenu_link_by_label(label: str) -> str:
    return (
        "xpath=//ul[contains(@class,'submenu')]"
        f"//span[normalize-space()='{label}']"
        "/ancestor::a[contains(@class,'nav-link')][1]"
    )


def _sidebar_link_by_href(fragment: str, *, exclude_fragment: str | None = None) -> str:
    if exclude_fragment:
        return (
            f"xpath=//a[contains(@href,'{fragment}') "
            f"and not(contains(@href,'{exclude_fragment}'))]"
        )
    return f"a[href*='{fragment}']"


def _sidebar_child_link(parent_label: str, child_label: str) -> str:
    """Leaf/toggle link under a top-level sidebar section (e.g. Pricing > Common)."""
    return (
        "xpath=//a[contains(@class,'nav-link')]"
        f"[.//span[normalize-space()='{parent_label}']]"
        "/ancestor::li[1]"
        "//ul[contains(@class,'submenu') or contains(@class,'menu-content')]"
        f"//span[normalize-space()='{child_label}']"
        "/ancestor::a[contains(@class,'nav-link')][1]"
    )


def etms_page_title_selectors(title: str) -> list[str]:
    """Page title locators — ITL (h3.page-title) and VFC (h5.semibold / breadcrumb)."""
    return [
        f"xpath=//h3[normalize-space()='{title}']",
        f"h3:has-text('{title}')",
        f"xpath=//h5[normalize-space()='{title}']",
        f"h5:has-text('{title}')",
        f".page-title:has-text('{title}')",
        f"xpath=//*[contains(@class,'page-title') and normalize-space()='{title}']",
        (
            "xpath=//li[contains(@class,'breadcrumb-item') and contains(@class,'active')]"
            f"//span[normalize-space()='{title}']"
        ),
        (
            "xpath=//*[contains(@class,'page-title') "
            f"and contains(normalize-space(),'{title}')]"
        ),
    ]


def etms_pricing_filter_tab_selectors(tab_label: str) -> list[str]:
    """Pricing workflow tabs — VFC uses button/span inside ul.filter-tab; ITL may use anchor."""
    lit = tab_label.strip()
    return [
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//button[normalize-space()='{lit}']"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//button[.//span[normalize-space()='{lit}']]"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//span[normalize-space()='{lit}']"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//a[normalize-space()='{lit}']"
        ),
        (
            "xpath=//ul[contains(@class,'filter-tab')]"
            f"//a[.//span[normalize-space()='{lit}']]"
        ),
        (
            f"xpath=//*[self::button or self::span or self::a]"
            f"[normalize-space()='{lit}' and ancestor::ul[contains(@class,'filter-tab')]]"
        ),
    ]


def etms_in_page_tab_selectors(tab_label: str) -> list[str]:
    """In-page tab locators — ITL (nav-tabs) and VFC (main-content a.nav-link)."""
    return [
        (
            "xpath=//div[contains(@class,'nav-tabs')]"
            f"//a[normalize-space()='{tab_label}']"
        ),
        (
            "xpath=//ul[contains(@class,'nav-tabs')]"
            f"//a[normalize-space()='{tab_label}']"
        ),
        (
            f"xpath=//a[contains(@class,'nav-link') and normalize-space()='{tab_label}' "
            "and not(ancestor::lth-sidebar) and not(ancestor::*[contains(@class,'sidebar-menu')])]"
        ),
        f"xpath=//*[@role='tab' and normalize-space()='{tab_label}']",
        (
            "xpath=//div[contains(@class,'ant-tabs-tab')]"
            f"[normalize-space()='{tab_label}']"
        ),
        (
            "xpath=//*[self::h3 or contains(@class,'page-title')]"
            "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            f"//a[contains(@class,'nav-link') and normalize-space()='{tab_label}']"
        ),
        f"text='{tab_label}'",
    ]


class EtmsCatalogueMenuPage(BasePage):
    """Sidebar navigation — Catalogue menu group (eTMS nav-link sidebar)."""

    loading_overlay_selectors = [
        ".m-blockui",
        ".block-ui-wrapper.block-ui-active",
        "xpath=//div[contains(@class,'block-ui') and contains(@class,'active')]",
        "xpath=//div[contains(@class,'loading-mask')]",
        ".ng-progress-bar[active='true']",
    ]

    sidebar_ready_selectors = [
        "#cat > a.nav-link",
        "xpath=//li[@id='cat']//span[normalize-space()='Catalogue']",
        _sidebar_link_by_label("Catalogue"),
        "lth-sidebar .sidebar-menu",
        ".ftl-main-header",
    ]

    catalogue_menu_selectors = [
        "#cat > a.nav-link",
        (
            "xpath=//li[@id='cat']//span[normalize-space()='Catalogue']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _sidebar_link_by_label("Catalogue"),
    ]

    catalogue_expanded_selectors = [
        "#catTransportNetwork > a.nav-link",
        "#catPartners > a.nav-link",
        "#catVehicles > a.nav-link",
        "#catDrivers > a.nav-link",
        "#catCommoditys > a.nav-link",
        _catalogue_submenu_link_by_label("Transport Network"),
        _catalogue_submenu_link_by_label("Partner"),
        _catalogue_submenu_link_by_label("Vehicle"),
        _catalogue_submenu_link_by_label("Driver list"),
        _catalogue_submenu_link_by_label("Commodity"),
        _sidebar_link_by_href("catalogue/charge"),
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
        _catalogue_submenu_link_by_label("Transport Network"),
    ]

    transport_network_submenu_selectors = [
        "#catOtherPlace > a.nav-link",
        (
            "xpath=//li[@id='catTransportNetwork']"
            "//li[@id='catOtherPlace']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_href("catalogue/other-place"),
        _sidebar_link_by_label("Places"),
    ]

    partner_toggle_selectors = [
        "#catPartners > a.nav-link",
        (
            "xpath=//li[@id='catPartners']"
            "//span[normalize-space()='Partner']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Partner"),
    ]

    partner_submenu_selectors = [
        "#catPartnerGroup > a.nav-link",
        (
            "xpath=//li[@id='catPartners']"
            "//li[@id='catPartnerGroup']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_href("catalogue/partner-group"),
        _sidebar_link_by_label("Partner Group"),
    ]

    vehicle_toggle_selectors = [
        "#catVehicles > a.nav-link",
        (
            "xpath=//li[@id='catVehicles']"
            "//span[normalize-space()='Vehicle']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Vehicle"),
    ]

    vehicle_submenu_selectors = [
        "#catVehicle > a.nav-link",
        (
            "xpath=//li[@id='catVehicles']"
            "//li[@id='catVehicle']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_label("Vehicle List"),
        (
            "xpath=//a[contains(@href,'catalogue/vehicle') "
            "and not(contains(@href,'vehicle-'))]"
        ),
    ]

    driver_toggle_selectors = [
        "#catDrivers > a.nav-link",
        (
            "xpath=//li[@id='catDrivers']"
            "//span[normalize-space()='Driver list']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Driver list"),
    ]

    driver_submenu_selectors = [
        "#catDriver > a.nav-link",
        (
            "xpath=//li[@id='catDrivers']"
            "//li[@id='catDriver']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_href("catalogue/driver"),
        _sidebar_link_by_label("Driver"),
    ]

    commodity_toggle_selectors = [
        "#catCommoditys > a.nav-link",
        (
            "xpath=//li[@id='catCommoditys']"
            "//span[normalize-space()='Commodity']"
            "/ancestor::a[contains(@class,'nav-link')][1]"
        ),
        _catalogue_submenu_link_by_label("Commodity"),
    ]

    commodity_submenu_selectors = [
        "#catCommodity > a.nav-link",
        (
            "xpath=//li[@id='catCommoditys']"
            "//li[@id='catCommodity']//a[contains(@class,'nav-link')]"
        ),
        _sidebar_link_by_label("Commodity List"),
        (
            "xpath=//a[contains(@href,'catalogue/commodity') "
            "and not(contains(@href,'commodity-'))]"
        ),
    ]

    pricing_menu_selectors = [
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Pricing']]",
        _sidebar_link_by_label("Pricing"),
    ]

    pricing_expanded_selectors = [
        _sidebar_child_link("Pricing", "Common"),
        _sidebar_child_link("Pricing", "FCL Pricing"),
        _sidebar_child_link("Pricing", "LCL Pricing"),
        _sidebar_link_by_href("pricing/common"),
        _sidebar_link_by_href("pricing/fcl"),
        _sidebar_link_by_href("pricing/rate-card-list"),
    ]

    pricing_common_toggle_selectors = [
        _sidebar_child_link("Pricing", "Common"),
        _sidebar_link_by_href("pricing/common"),
    ]

    pricing_common_expanded_selectors = [
        _sidebar_link_by_href("pricing/cost-of-route"),
        _sidebar_link_by_href("pricing/toll-buying"),
        _sidebar_child_link("Pricing", "Cost Of Route"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='Cost Of Route']]",
    ]

    pricing_fcl_toggle_selectors = [
        _sidebar_child_link("Pricing", "FCL Pricing"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL Pricing']]",
    ]

    pricing_fcl_expanded_selectors = [
        _sidebar_link_by_href("pricing/fcl/fcl-rate-card-list"),
        _sidebar_link_by_href("pricing/fcl/fcl-buying"),
        _sidebar_link_by_href("pricing/fcl/fcl-renting-container"),
        _sidebar_link_by_href("pricing/fcl/fcl-renting-vehicle"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='FCL Rate Card List']]",
    ]

    pricing_lcl_toggle_selectors = [
        _sidebar_child_link("Pricing", "LCL Pricing"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL Pricing']]",
    ]

    pricing_lcl_expanded_selectors = [
        _sidebar_link_by_href("pricing/rate-card-list"),
        _sidebar_link_by_href("pricing/buying"),
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='3. LCL Rate Card']]",
        "xpath=//a[contains(@class,'nav-link')][.//span[normalize-space()='LCL Buying']]",
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

    def wait_for_catalogue_idle(self, timeout: int | None = None) -> "EtmsCatalogueMenuPage":
        """Wait until block-ui / loading overlays are gone before sidebar navigation."""
        timeout = timeout or settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if self.find_visible(self.loading_overlay_selectors) is None:
                return self
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(
            f"Catalogue page still loading — overlay active after {timeout}ms"
        )

    def _wait_for_url_hash(self, page_hash: str, timeout: int | None = None) -> None:
        timeout = timeout or settings.page_load_timeout
        normalized_hash = page_hash.lower().replace("_", "-")
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            if normalized_hash in self.current_url.lower().replace("_", "-"):
                return
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(
            f"URL hash '{page_hash}' not found after {timeout}ms. "
            f"Current URL: {self.current_url}"
        )

    def wait_before_next_catalogue_navigation(self) -> "EtmsCatalogueMenuPage":
        """Ensure current page data/overlay finished before clicking another menu."""
        self.wait_for_catalogue_idle()
        self.wait_for_page_stable()
        return self

    def _scroll_sidebar_link_into_view(self, link: Locator) -> None:
        """Scroll nested sidebar menu containers so leaf items (e.g. Currency) are clickable."""
        link.evaluate(
            "(el) => el.scrollIntoView({ block: 'center', inline: 'nearest' })"
        )
        link.scroll_into_view_if_needed()

    def _find_sidebar_link(self, selectors: list[str]) -> Locator | None:
        """Resolve nested sidebar links that exist in DOM but sit below the fold."""
        for selector in selectors:
            locator = self.page.locator(selector).first
            try:
                if locator.count() == 0:
                    continue
                self._scroll_sidebar_link_into_view(locator)
                if locator.is_visible():
                    logger.info(f"Found sidebar link by selector: {selector}")
                    return locator
            except Exception:
                continue
        return None

    def _click_sidebar_link(self, selectors: list[str], element_name: str) -> None:
        self.wait_before_next_catalogue_navigation()
        timeout = settings.browser_timeout
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            link = self._find_sidebar_link(selectors)
            if link is not None:
                self.wait_for_page_stable()
                link.click(force=True)
                self.wait_for_page_stable()
                return
            self.page.wait_for_timeout(settings.polling_interval)
        raise AssertionError(self._build_wait_error(element_name, selectors, timeout))

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

    @log_method("Open Vehicle menu")
    def open_vehicle_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.vehicle_toggle_selectors,
            submenu_selectors=self.vehicle_submenu_selectors,
            toggle_label="Vehicle menu",
            ready_label="Vehicle List menu under Vehicle",
        )

    @log_method("Open Driver list menu")
    def open_driver_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.driver_toggle_selectors,
            submenu_selectors=self.driver_submenu_selectors,
            toggle_label="Driver list menu",
            ready_label="Driver menu under Driver list",
        )

    @log_method("Open Commodity menu")
    def open_commodity_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_catalogue_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.commodity_toggle_selectors,
            submenu_selectors=self.commodity_submenu_selectors,
            toggle_label="Commodity menu",
            ready_label="Commodity List menu under Commodity",
        )

    @log_method("Open Pricing menu")
    def open_pricing_menu(self) -> "EtmsCatalogueMenuPage":
        self.wait_for_sidebar_ready()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_menu_selectors,
            submenu_selectors=self.pricing_expanded_selectors,
            toggle_label="Pricing menu",
            ready_label="Pricing submenu",
        )

    @log_method("Open Pricing > Common menu")
    def open_pricing_common_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_common_toggle_selectors,
            submenu_selectors=self.pricing_common_expanded_selectors,
            toggle_label="Common menu under Pricing",
            ready_label="Cost Of Route menu under Common",
        )

    @log_method("Open Pricing > FCL Pricing menu")
    def open_pricing_fcl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_fcl_toggle_selectors,
            submenu_selectors=self.pricing_fcl_expanded_selectors,
            toggle_label="FCL Pricing menu under Pricing",
            ready_label="FCL Rate Card List menu under FCL Pricing",
        )

    @log_method("Open Pricing > LCL Pricing menu")
    def open_pricing_lcl_menu(self) -> "EtmsCatalogueMenuPage":
        self.open_pricing_menu()
        return self._open_sidebar_submenu(
            toggle_selectors=self.pricing_lcl_toggle_selectors,
            submenu_selectors=self.pricing_lcl_expanded_selectors,
            toggle_label="LCL Pricing menu under Pricing",
            ready_label="3. LCL Rate Card menu under LCL Pricing",
        )
