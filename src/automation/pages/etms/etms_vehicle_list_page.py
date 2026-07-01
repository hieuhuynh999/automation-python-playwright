from __future__ import annotations

from automation.logging import log_method
from automation.pages.etms.etms_catalogue_tabbed_list_page import (
    EtmsCatalogueTabConfig,
    EtmsCatalogueTabbedListPage,
)

ETMS_VEHICLE_LIST_TAB_CONFIGS: dict[str, EtmsCatalogueTabConfig] = {
    "internal": EtmsCatalogueTabConfig(
        tab_key="internal",
        tab_label="Internal",
        list_column_headers=("License Plate", "Vehicle Type"),
    ),
    "external": EtmsCatalogueTabConfig(
        tab_key="external",
        tab_label="External",
        list_column_headers=("License Plate", "Vehicle Type"),
    ),
}

DEFAULT_ETMS_VEHICLE_LIST_TAB = "internal"


class EtmsVehicleListPage(EtmsCatalogueTabbedListPage):
    """Vehicle List — Catalogue > Vehicle > Internal / External tabs."""

    page_key = "vehicle_list"
    page_hash = "catalogue/vehicle"
    title = "Vehicle List"
    menu_li_id = "catVehicle"
    default_tab_key = DEFAULT_ETMS_VEHICLE_LIST_TAB
    tab_configs = ETMS_VEHICLE_LIST_TAB_CONFIGS
    _landing_tab_key = "internal"

    def list_table_selectors_for_tab(self, tab_key: str) -> list[str]:
        config = self._tab_config(tab_key)
        first_header = config.list_column_headers[0]
        tab_label = config.tab_label
        return [
            (
                "xpath=//div[contains(@class,'tab-content')]"
                "//div[contains(@class,'tab-pane') and contains(@class,'active')]"
                f"//table[.//th[normalize-space()='{first_header}']]//th"
            ),
            (
                "xpath=//div[contains(@class,'nav-tabs')]"
                f"//a[contains(@class,'active') and normalize-space()='{tab_label}']"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//table[.//th[normalize-space()='{first_header}']]//th",
            (
                f"xpath=//*[self::h3 or contains(@class,'page-title')]"
                f"[normalize-space()='{self.title}' or contains(normalize-space(),'{self.title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    def _ensure_tab_active(self, tab_key: str) -> None:
        if tab_key == self._landing_tab_key:
            return
        self._activate_tab(tab_key)

    @log_method("Click Vehicle List menu")
    def click_menu(
        self,
        tab_key: str = DEFAULT_ETMS_VEHICLE_LIST_TAB,
    ) -> EtmsVehicleListPage:
        self.open_vehicle_menu()
        self._navigate_to_page()
        self._ensure_tab_active(tab_key)
        self._wait_tab_grid(tab_key, min_rows=1)
        return self
