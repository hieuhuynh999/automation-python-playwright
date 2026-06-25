from __future__ import annotations

from automation.logging import log_method
from automation.pages.etms.etms_catalogue_tabbed_list_page import (
    EtmsCatalogueTabConfig,
    EtmsCatalogueTabbedListPage,
)

ETMS_ZONE_CODE_TAB_CONFIGS: dict[str, EtmsCatalogueTabConfig] = {
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

DEFAULT_ETMS_ZONE_CODE_TAB = "pickup_zone_code"

# Backward-compatible aliases
ZONE_CODE_TAB_CONFIGS = ETMS_ZONE_CODE_TAB_CONFIGS
DEFAULT_ZONE_CODE_TAB = DEFAULT_ETMS_ZONE_CODE_TAB
ZoneCodeTabConfig = EtmsCatalogueTabConfig


class EtmsZoneCodePage(EtmsCatalogueTabbedListPage):
    """Zone Code — Catalogue > Transport Network > Pickup / Delivery tabs."""

    page_key = "zone_code"
    page_hash = "catalogue/zone-code"
    title = "Zone Code"
    menu_li_id = "catZoneCode"
    default_tab_key = DEFAULT_ETMS_ZONE_CODE_TAB
    tab_configs = ETMS_ZONE_CODE_TAB_CONFIGS

    list_title_selectors = [
        "xpath=//h3[normalize-space()='Zone Code']",
        "h3:has-text('Zone Code')",
        ".page-title:has-text('Zone Code')",
    ]

    def _tab_selectors(self, tab_label: str) -> list[str]:
        return [
            f"text='{tab_label}'",
            (
                "xpath=//*[self::h3 or contains(@class,'page-title')]"
                f"[normalize-space()='{self.title}' or contains(normalize-space(),'{self.title}')]"
                f"/following::*[normalize-space()='{tab_label}'][1]"
            ),
            (
                "xpath=//div[contains(@class,'tab-content')]"
                f"/preceding-sibling::*[contains(@class,'nav') or contains(@class,'tab')]"
                f"//*[normalize-space()='{tab_label}']"
            ),
            (
                "xpath=//div[contains(@class,'nav-tabs')]"
                f"//a[normalize-space()='{tab_label}']"
            ),
        ]

    @log_method("Click Zone Code menu")
    def click_menu(self, tab_key: str = DEFAULT_ETMS_ZONE_CODE_TAB) -> EtmsZoneCodePage:
        self.open_transport_network_menu()
        self._navigate_to_page()
        self._activate_tab(tab_key)
        self._wait_tab_grid(tab_key, min_rows=1)
        return self

    def load_page_for_performance(
        self,
        min_rows: int = 1,
        *,
        tab_key: str | None = None,
    ) -> EtmsZoneCodePage:
        active_tab = tab_key or DEFAULT_ETMS_ZONE_CODE_TAB
        self._navigate_to_page()
        self._activate_tab(active_tab)
        self._wait_tab_grid(active_tab, min_rows)
        return self
