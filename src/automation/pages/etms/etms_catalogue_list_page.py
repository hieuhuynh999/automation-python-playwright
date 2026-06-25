from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from automation.config import settings
from automation.logging import log_method
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import (
    EtmsCatalogueMenuPage,
    _catalogue_submenu_link_by_label,
    _sidebar_link_by_href,
    etms_page_title_selectors,
)

EtmsCatalogueSuite = Literal[
    "transport_network",
    "partner",
    "vehicle",
    "driver",
    "commodity",
    "catalogue_master",
]


@dataclass(frozen=True)
class EtmsCatalogueListPageConfig:
    page_key: str
    title: str
    page_hash: str
    menu_li_id: str
    list_column_headers: tuple[str, ...]
    catalogue_suite: EtmsCatalogueSuite = "transport_network"


TRANSPORT_NETWORK_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "places": EtmsCatalogueListPageConfig(
        page_key="places",
        title="Places",
        page_hash="catalogue/other-place",
        menu_li_id="catOtherPlace",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "distance_between_places": EtmsCatalogueListPageConfig(
        page_key="distance_between_places",
        title="Distance Between Places",
        page_hash="catalogue/distance-between-places",
        menu_li_id="catPlaceDistance",
        list_column_headers=("Place From", "Place To"),
    ),
    "route_information": EtmsCatalogueListPageConfig(
        page_key="route_information",
        title="Route Information",
        page_hash="catalogue/route-infomation",
        menu_li_id="catRoute",
        list_column_headers=("Code", "Place From"),
    ),
    "transit_route": EtmsCatalogueListPageConfig(
        page_key="transit_route",
        title="Transit Route",
        page_hash="catalogue/transit-route",
        menu_li_id="catTransitRouteMiddlePlace",
        list_column_headers=("Code", "POL"),
    ),
    "hub": EtmsCatalogueListPageConfig(
        page_key="hub",
        title="Hub",
        page_hash="catalogue/hub",
        menu_li_id="sysHub",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "branch": EtmsCatalogueListPageConfig(
        page_key="branch",
        title="Branch",
        page_hash="catalogue/branch",
        menu_li_id="sysBranch",
        list_column_headers=("Code", "Name (VI)"),
    ),
    "route_project_information": EtmsCatalogueListPageConfig(
        page_key="route_project_information",
        title="Route Project Information",
        page_hash="catalogue/route-project",
        menu_li_id="catRouteProject",
        list_column_headers=("Customer", "Project Code"),
    ),
}

PARTNER_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "partner_group": EtmsCatalogueListPageConfig(
        page_key="partner_group",
        title="Partner Group",
        page_hash="catalogue/partner-group",
        menu_li_id="catPartnerGroup",
        list_column_headers=("Code", "Group name (VI)"),
        catalogue_suite="partner",
    ),
    "partner_list": EtmsCatalogueListPageConfig(
        page_key="partner_list",
        title="Partner list",
        page_hash="catalogue/partner-list",
        menu_li_id="catPartner",
        list_column_headers=("Partner Group", "ID"),
        catalogue_suite="partner",
    ),
    "bank_account": EtmsCatalogueListPageConfig(
        page_key="bank_account",
        title="Bank Account",
        page_hash="catalogue/partner-account-bank",
        menu_li_id="catAccountBankOfPartner",
        list_column_headers=("Partner Group", "Partner Name"),
        catalogue_suite="partner",
    ),
}

VEHICLE_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "vehicle_list": EtmsCatalogueListPageConfig(
        page_key="vehicle_list",
        title="Vehicle List",
        page_hash="catalogue/vehicle",
        menu_li_id="catVehicle",
        list_column_headers=("License Plate", "Vehicle Type"),
        catalogue_suite="vehicle",
    ),
}

DRIVER_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "driver": EtmsCatalogueListPageConfig(
        page_key="driver",
        title="Driver",
        page_hash="catalogue/driver",
        menu_li_id="catDriver",
        list_column_headers=("ID", "Driver Name (VI)"),
        catalogue_suite="driver",
    ),
    "driver_vehicle": EtmsCatalogueListPageConfig(
        page_key="driver_vehicle",
        title="Driver - Vehicle",
        page_hash="catalogue/vehicle-driver",
        menu_li_id="catVehicleDriver",
        list_column_headers=("Driver", "Vehicle"),
        catalogue_suite="driver",
    ),
}

COMMODITY_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "commodity_list": EtmsCatalogueListPageConfig(
        page_key="commodity_list",
        title="Commodity List",
        page_hash="catalogue/commodity",
        menu_li_id="catCommodity",
        list_column_headers=("Name (VI)", "Name (EN)"),
        catalogue_suite="commodity",
    ),
    "commodity_group": EtmsCatalogueListPageConfig(
        page_key="commodity_group",
        title="Commodity Group",
        page_hash="catalogue/commodity-group",
        menu_li_id="catCommodityGroup",
        list_column_headers=("Name (VI)", "Name (EN)"),
        catalogue_suite="commodity",
    ),
}

CATALOGUE_MASTER_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "charge_list": EtmsCatalogueListPageConfig(
        page_key="charge_list",
        title="Charge List",
        page_hash="catalogue/charge",
        menu_li_id="catCharge",
        list_column_headers=("ID", "Name (VI)"),
        catalogue_suite="catalogue_master",
    ),
    "unit": EtmsCatalogueListPageConfig(
        page_key="unit",
        title="Unit",
        page_hash="catalogue/unit",
        menu_li_id="catUnit",
        list_column_headers=("Code", "Name (VI)"),
        catalogue_suite="catalogue_master",
    ),
    "service_type": EtmsCatalogueListPageConfig(
        page_key="service_type",
        title="Service Type",
        page_hash="catalogue/service-type",
        menu_li_id="catServiceType",
        list_column_headers=("Code", "Name"),
        catalogue_suite="catalogue_master",
    ),
    "weight_range": EtmsCatalogueListPageConfig(
        page_key="weight_range",
        title="Weight Range",
        page_hash="catalogue/weigth-range",
        menu_li_id="catWeightRange",
        list_column_headers=("Min Weight", "Max Weight"),
        catalogue_suite="catalogue_master",
    ),
    "container_type": EtmsCatalogueListPageConfig(
        page_key="container_type",
        title="Container Type",
        page_hash="catalogue/container-type",
        menu_li_id="catContainerType",
        list_column_headers=("ID", "Name"),
        catalogue_suite="catalogue_master",
    ),
    "container": EtmsCatalogueListPageConfig(
        page_key="container",
        title="Container",
        page_hash="catalogue/container-list",
        menu_li_id="catContainer",
        list_column_headers=("Container No", "Container Type"),
        catalogue_suite="catalogue_master",
    ),
    "currency": EtmsCatalogueListPageConfig(
        page_key="currency",
        title="Currency",
        page_hash="catalogue/currency",
        menu_li_id="catCurrency",
        list_column_headers=("To Currency", "Rate"),
        catalogue_suite="catalogue_master",
    ),
}

CATALOGUE_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    **TRANSPORT_NETWORK_LIST_PAGE_CONFIGS,
    **PARTNER_LIST_PAGE_CONFIGS,
    **VEHICLE_LIST_PAGE_CONFIGS,
    **DRIVER_LIST_PAGE_CONFIGS,
    **COMMODITY_LIST_PAGE_CONFIGS,
    **CATALOGUE_MASTER_LIST_PAGE_CONFIGS,
}


class EtmsCatalogueListPage(EtmsCatalogueMenuPage):
    """Generic catalogue list page — Transport Network or Partner submenu."""

    def __init__(self, page, page_key: str) -> None:
        super().__init__(page)
        if page_key not in CATALOGUE_LIST_PAGE_CONFIGS:
            known = ", ".join(sorted(CATALOGUE_LIST_PAGE_CONFIGS))
            raise ValueError(f"Unknown catalogue list page_key '{page_key}'. Known: {known}")
        self._config = CATALOGUE_LIST_PAGE_CONFIGS[page_key]
        self.page_key = page_key
        self.page_hash = self._config.page_hash

    @property
    def list_grid(self) -> ListGridComponent:
        attr = f"_list_grid_{self.page_key}"
        if not hasattr(self, attr):
            setattr(
                self,
                attr,
                ListGridComponent(self, f"{self._config.title} list grid"),
            )
        return getattr(self, attr)

    @property
    def list_table_selectors(self) -> list[str]:
        return self._list_table_selectors()

    def _open_catalogue_suite_menu(self) -> None:
        if self._config.catalogue_suite == "partner":
            self.open_partner_menu()
        elif self._config.catalogue_suite == "vehicle":
            self.open_vehicle_menu()
        elif self._config.catalogue_suite == "driver":
            self.open_driver_menu()
        elif self._config.catalogue_suite == "commodity":
            self.open_commodity_menu()
        elif self._config.catalogue_suite == "catalogue_master":
            self.open_catalogue_menu()
        else:
            self.open_transport_network_menu()

    def _menu_selectors(self) -> list[str]:
        title = self._config.title
        menu_li_id = self._config.menu_li_id
        page_hash = self._config.page_hash
        return [
            f"#{menu_li_id} > a.nav-link",
            _catalogue_submenu_link_by_label(title),
            (
                f"xpath=//li[@id='{menu_li_id}']"
                f"//span[normalize-space()='{title}']"
                "/ancestor::a[contains(@class,'nav-link')][1]"
            ),
            (
                "xpath=//a[contains(@class,'nav-link')]"
                f"[.//span[normalize-space()='{title}']]"
            ),
            _sidebar_link_by_href(page_hash),
        ]

    def _list_title_selectors(self) -> list[str]:
        return etms_page_title_selectors(self._config.title)

    def _list_table_selectors(self) -> list[str]:
        title = self._config.title
        first_header = self._config.list_column_headers[0]
        return [
            f"xpath=//table[.//th[normalize-space()='{first_header}']]//th",
            (
                f"xpath=//*[self::h3 or contains(@class,'page-title')]"
                f"[normalize-space()='{title}' or contains(normalize-space(),'{title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
                "//table//th"
            ),
            f"xpath=//th[normalize-space()='{first_header}']",
        ]

    def _navigate_to_list_page(self) -> None:
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self._config.title} menu",
        )
        self._wait_for_url_hash(self.page_hash)
        self.wait_for_page_stable()

    def confirm_grid_loaded(
        self,
        min_rows: int = 1,
        *,
        allow_no_data: bool = False,
    ) -> EtmsCatalogueListPage:
        """Re-verify list grid is ready — call before navigating to the next catalogue page."""
        self.wait_before_next_catalogue_navigation()
        self._wait_for_list_grid(min_rows)
        return self

    def _wait_for_list_grid(self, min_rows: int) -> None:
        self.wait_for_visible(
            self._list_title_selectors(),
            f"{self._config.title} page title",
        )
        self.list_grid.wait_until_ready(
            self.list_table_selectors,
            f"{self._config.title} table",
        )
        self.list_grid.verify_column_headers(
            list(self._config.list_column_headers),
            table_selectors=self.list_table_selectors,
        )
        self.list_grid.wait_for_data_rows(
            min_rows=min_rows,
            table_selectors=self.list_table_selectors,
        )

    @log_method("Click catalogue list menu")
    def click_menu(self) -> EtmsCatalogueListPage:
        self._open_catalogue_suite_menu()
        self._navigate_to_list_page()
        self._wait_for_list_grid(min_rows=1)
        return self

    def prepare_for_performance(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
    ) -> str:
        """Submenu is opened by the performance suite — timed step is sidebar click → data."""
        del tab_key, min_rows, allow_no_data
        return "click"

    def run_performance_measurement(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        mode: str = "click",
    ) -> None:
        """Timed segment: sidebar menu click → list grid data displayed."""
        del tab_key, allow_no_data
        if mode == "skipped":
            return
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self._config.title} menu",
        )
        self._wait_for_url_hash(self.page_hash)
        self.wait_for_page_stable()
        self._wait_for_list_grid(min_rows)

    def load_page_for_performance(self, min_rows: int = 1) -> EtmsCatalogueListPage:
        """Click menu and wait for table — used by performance tests (no POM step logs)."""
        mode = self.prepare_for_performance(min_rows=min_rows)
        self.run_performance_measurement(min_rows=min_rows, mode=mode)
        return self


# Backward-compatible aliases (deprecated — prefer EtmsCatalogueListPage*)
EtmsTransportNetworkListPage = EtmsCatalogueListPage
EtmsPartnerListPage = EtmsCatalogueListPage
TransportNetworkListPageConfig = EtmsCatalogueListPageConfig
PartnerListPageConfig = EtmsCatalogueListPageConfig
