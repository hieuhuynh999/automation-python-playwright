from __future__ import annotations

from automation.logging import log_method
from automation.pages.etms.etms_catalogue_menu_page import (
    _catalogue_submenu_link_by_label,
    _sidebar_link_by_href,
    etms_in_page_tab_selectors,
)
from automation.pages.etms.etms_catalogue_tabbed_list_page import (
    EtmsCatalogueTabConfig,
    EtmsCatalogueTabbedListPage,
)

ETMS_ZONE_CODE_TAB_CONFIGS: dict[str, EtmsCatalogueTabConfig] = {
    "zone_code": EtmsCatalogueTabConfig(
        tab_key="zone_code",
        tab_label="Zone Code",
        list_column_headers=("Code", "Type"),
    ),
    "pickup_zone_code": EtmsCatalogueTabConfig(
        tab_key="pickup_zone_code",
        tab_label="Pickup Zone Code",
        list_column_headers=("Pickup Place", "District"),
    ),
    "delivery_zone_code": EtmsCatalogueTabConfig(
        tab_key="delivery_zone_code",
        tab_label="Delivery Zone Code",
        list_column_headers=("To Place", "District"),
    ),
}

DEFAULT_ETMS_ZONE_CODE_TAB = "zone_code"

# Backward-compatible aliases
ZONE_CODE_TAB_CONFIGS = ETMS_ZONE_CODE_TAB_CONFIGS
DEFAULT_ZONE_CODE_TAB = DEFAULT_ETMS_ZONE_CODE_TAB
ZoneCodeTabConfig = EtmsCatalogueTabConfig


class EtmsZoneCodePage(EtmsCatalogueTabbedListPage):
    """Zone Code — Catalogue > Transport Network > Zone Code / Pickup / Delivery tabs."""

    page_key = "zone_code"
    page_hash = "catalogue/zone-code"
    title = "Zone Code"
    menu_li_id = "catZoneCode"
    default_tab_key = DEFAULT_ETMS_ZONE_CODE_TAB
    tab_configs = ETMS_ZONE_CODE_TAB_CONFIGS
    _landing_tab_key = "zone_code"

    def _is_on_zone_code_page(self) -> bool:
        hash_fragment = self.page_hash.lower().replace("_", "-")
        return hash_fragment in self.current_url.lower().replace("_", "-")

    def _menu_selectors(self) -> list[str]:
        return [
            f"#{self.menu_li_id} > a.nav-link",
            _catalogue_submenu_link_by_label(self.title),
            _sidebar_link_by_href(self.page_hash, exclude_fragment="delivery"),
            (
                "xpath=//a[contains(@class,'nav-link')]"
                f"[.//span[normalize-space()='{self.title}']]"
            ),
        ]

    def _tab_selectors(self, tab_label: str) -> list[str]:
        title = self.title
        return [
            (
                "xpath=//div[contains(@class,'nav-tabs')]"
                f"//a[normalize-space()='{tab_label}']"
            ),
            (
                "xpath=//*[self::h3 or self::h5 or contains(@class,'page-title')]"
                f"[normalize-space()='{title}' or contains(normalize-space(),'{title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                f"//div[contains(@class,'nav-tabs')]//a[normalize-space()='{tab_label}']"
            ),
            (
                "xpath=//div[contains(@class,'main-content')]"
                f"//a[contains(@class,'nav-link') and normalize-space()='{tab_label}' "
                "and not(ancestor::lth-sidebar) and not(ancestor::*[contains(@class,'sidebar-menu')])]"
            ),
            *etms_in_page_tab_selectors(tab_label),
        ]

    def list_table_selectors_for_tab(self, tab_key: str) -> list[str]:
        config = self._tab_config(tab_key)
        first_header = config.list_column_headers[0]
        tab_label = config.tab_label
        return [
            f"xpath=//table[.//th[normalize-space()='{first_header}']]//th",
            (
                "xpath=//div[contains(@class,'nav-tabs')]"
                f"//a[contains(@class,'active') and normalize-space()='{tab_label}']"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            (
                "xpath=//*[self::h3 or self::h5 or contains(@class,'page-title')]"
                f"[normalize-space()='{self.title}' or contains(normalize-space(),'{self.title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    def _navigate_to_page(self, tab_key: str | None = None) -> None:
        if self._is_on_zone_code_page():
            return
        self._navigate_to_page_hash(
            self.page_hash,
            self._menu_selectors(),
            f"{self.title} menu",
            self.title,
        )

    def _ensure_tab_active(self, tab_key: str) -> None:
        if tab_key == self._landing_tab_key and self._is_on_zone_code_page():
            return
        self._activate_tab(tab_key)

    @log_method("Click Zone Code menu")
    def click_menu(self, tab_key: str = DEFAULT_ETMS_ZONE_CODE_TAB) -> EtmsZoneCodePage:
        self.open_transport_network_menu()
        self._navigate_to_page(tab_key)
        self._ensure_tab_active(tab_key)
        self._wait_tab_grid(tab_key, min_rows=1)
        return self
