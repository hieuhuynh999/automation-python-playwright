from __future__ import annotations

from automation.logging import log_method
from automation.pages.etms.etms_catalogue_tabbed_list_page import (
    EtmsCatalogueTabConfig,
    EtmsCatalogueTabbedListPage,
)

ETMS_VEHICLE_TYPE_TAB_CONFIGS: dict[str, EtmsCatalogueTabConfig] = {
    "vehicle_group": EtmsCatalogueTabConfig(
        tab_key="vehicle_group",
        tab_label="Vehicle Group",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "vehicle_type_fuel_consumption": EtmsCatalogueTabConfig(
        tab_key="vehicle_type_fuel_consumption",
        tab_label="Vehicle Type - Fuel Consumption",
        list_column_headers=("Code", "Name (VI)"),
    ),
}

DEFAULT_ETMS_VEHICLE_TYPE_TAB = "vehicle_group"


class EtmsVehicleTypePage(EtmsCatalogueTabbedListPage):
    """Vehicle Type — Catalogue > Vehicle > Vehicle Group / Fuel Consumption tabs."""

    page_key = "vehicle_type"
    page_hash = "catalogue/vehicle-type"
    title = "Vehicle Type"
    menu_li_id = "catVehicleGroup"
    default_tab_key = DEFAULT_ETMS_VEHICLE_TYPE_TAB
    tab_configs = ETMS_VEHICLE_TYPE_TAB_CONFIGS
    _landing_tab_key = "vehicle_group"

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

    @log_method("Click Vehicle Type menu")
    def click_menu(
        self,
        tab_key: str = DEFAULT_ETMS_VEHICLE_TYPE_TAB,
    ) -> EtmsVehicleTypePage:
        self.open_vehicle_menu()
        self._navigate_to_page()
        self._ensure_tab_active(tab_key)
        self._wait_tab_grid(tab_key, min_rows=1)
        return self
