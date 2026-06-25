from __future__ import annotations

from automation.logging import log_method
from automation.pages.etms.etms_catalogue_tabbed_list_page import (
    EtmsCatalogueTabConfig,
    EtmsCatalogueTabbedListPage,
)

ETMS_ADMINISTRATIVE_UNITS_TAB_CONFIGS: dict[str, EtmsCatalogueTabConfig] = {
    "country": EtmsCatalogueTabConfig(
        tab_key="country",
        tab_label="Country",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "area": EtmsCatalogueTabConfig(
        tab_key="area",
        tab_label="Area",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "province_city": EtmsCatalogueTabConfig(
        tab_key="province_city",
        tab_label="Province/City",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "district": EtmsCatalogueTabConfig(
        tab_key="district",
        tab_label="District",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "ward_commune": EtmsCatalogueTabConfig(
        tab_key="ward_commune",
        tab_label="Ward/Commune",
        list_column_headers=("Code", "Name (VI)"),
    ),
}

DEFAULT_ETMS_ADMINISTRATIVE_UNITS_TAB = "country"

# Backward-compatible aliases
ADMINISTRATIVE_UNITS_TAB_CONFIGS = ETMS_ADMINISTRATIVE_UNITS_TAB_CONFIGS
DEFAULT_ADMINISTRATIVE_UNITS_TAB = DEFAULT_ETMS_ADMINISTRATIVE_UNITS_TAB
AdministrativeUnitsTabConfig = EtmsCatalogueTabConfig


class EtmsAdministrativeUnitsPage(EtmsCatalogueTabbedListPage):
    """Administrative Units — Catalogue > Transport Network > tabs (Country, Area, …)."""

    page_key = "administrative_units"
    page_hash = "catalogue/administrative-units"
    title = "Administrative Units"
    menu_li_id = "catAdministrativeUnit"
    default_tab_key = DEFAULT_ETMS_ADMINISTRATIVE_UNITS_TAB
    tab_configs = ETMS_ADMINISTRATIVE_UNITS_TAB_CONFIGS
    _landing_tab_key = "country"

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
                "xpath=//*[self::h3 or contains(@class,'page-title')]"
                "[contains(normalize-space(),'Administrative Units')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    def _ensure_tab_active(self, tab_key: str) -> None:
        """Country is the landing tab — skip click when page opens on it."""
        if tab_key == self._landing_tab_key:
            return
        self._activate_tab(tab_key)

    @log_method("Click Administrative Units menu")
    def click_menu(
        self,
        tab_key: str = DEFAULT_ETMS_ADMINISTRATIVE_UNITS_TAB,
    ) -> EtmsAdministrativeUnitsPage:
        self.open_transport_network_menu()
        self._navigate_to_page()
        self._ensure_tab_active(tab_key)
        self._wait_tab_grid(tab_key, min_rows=1)
        return self
