from __future__ import annotations

from dataclasses import dataclass

from automation.config import settings
from automation.logging import log_method
from automation.pages.common.list_grid_component import ListGridComponent
from automation.pages.etms.etms_catalogue_menu_page import (
    EtmsCatalogueMenuPage,
    _catalogue_submenu_link_by_label,
    _sidebar_child_link,
    _sidebar_link_by_href,
    etms_page_title_selectors,
)


@dataclass(frozen=True)
class EtmsCatalogueListPageConfig:
    page_key: str
    title: str
    page_hash: str
    menu_li_id: str
    list_column_headers: tuple[str, ...]
    catalogue_suite: str = "transport_network"
    menu_parent_label: str = ""


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

CUSTOMER_SERVICE_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "verifying_booking": EtmsCatalogueListPageConfig(
        page_key="verifying_booking",
        title="Verifying Booking",
        page_hash="customer/waybill-pending",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="customer_service_common",
    ),
    "fcl_surcharge_behalf": EtmsCatalogueListPageConfig(
        page_key="fcl_surcharge_behalf",
        title="FCL Surcharge/ Behalf",
        page_hash="customer/fcl-surcharge-behalf",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="customer_service_fcl",
    ),
    "fcl_surcharge_behalf_fleet": EtmsCatalogueListPageConfig(
        page_key="fcl_surcharge_behalf_fleet",
        title="FCL Surcharge/ Behalf (Fleet)",
        page_hash="customer/fcl-surcharge-behalf-fleet",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="customer_service_fcl",
    ),
    "lcl_ftl_transport_surcharge": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_transport_surcharge",
        title="LCL/FTL Transport Surcharge",
        page_hash="customer/lcl-ftl-transport-surcharge",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="customer_service_lcl_ftl",
    ),
    "lcl_ftl_surcharge_behalf": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_surcharge_behalf",
        title="LCL/FTL Surcharge/Behalf",
        page_hash="customer/lcl-ftl-surcharge-behalf",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="customer_service_lcl_ftl",
    ),
    "lcl_ftl_surcharge_behalf_fleet": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_surcharge_behalf_fleet",
        title="LCL/FTL Surcharge/ Behalf (Fleet)",
        page_hash="customer/lcl-ftl-surcharge-behalf-fleet",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="customer_service_lcl_ftl",
    ),
}

OPERATION_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "update_transport_info": EtmsCatalogueListPageConfig(
        page_key="update_transport_info",
        title="Update transport info",
        page_hash="customer/transport-data-entry",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_common",
    ),
    "dispatching": EtmsCatalogueListPageConfig(
        page_key="dispatching",
        title="Dispatching",
        page_hash="operation/common/dispatching",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_common",
    ),
    "trip_settlement": EtmsCatalogueListPageConfig(
        page_key="trip_settlement",
        title="Trip Settlement",
        page_hash="operation/common/settlement",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_common",
    ),
    "fuel_closing": EtmsCatalogueListPageConfig(
        page_key="fuel_closing",
        title="Fuel Closing",
        page_hash="operation/common/fuel-checking",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_common",
    ),
    "fcl_transport_request_list": EtmsCatalogueListPageConfig(
        page_key="fcl_transport_request_list",
        title="FCL Transport Request List",
        page_hash="operation/fcl-transport-request",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_fcl",
    ),
    "lcl_ftl_transport_request_list": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_transport_request_list",
        title="LCL/FTL Transport Request List",
        page_hash="operation/lcl/lcl-ftl-transport",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_lcl_ftl",
        menu_parent_label="Operation",
    ),
    "lcl_ftl_pickup_run_sheet": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_pickup_run_sheet",
        title="2.Pickup Run Sheet",
        page_hash="operation/lcl/pickup-run-sheet",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_lcl_ftl",
        menu_parent_label="Operation",
    ),
    "lcl_ftl_revenue_protection": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_revenue_protection",
        title="4.Revenue Protection",
        page_hash="operation/lcl/revenue-protection",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_lcl_ftl",
        menu_parent_label="Operation",
    ),
    "lcl_ftl_routing": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_routing",
        title="5.Routing",
        page_hash="customer/lcl-routing",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_lcl_ftl",
        menu_parent_label="Operation",
    ),
    "lcl_ftl_consolidation": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_consolidation",
        title="6.Consolidation",
        page_hash="operation/lcl/consolidation",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_lcl_ftl",
        menu_parent_label="Operation",
    ),
    "lcl_ftl_transit": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_transit",
        title="8.Transit",
        page_hash="operation/lcl/transit",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_lcl_ftl",
        menu_parent_label="Operation",
    ),
    "lcl_ftl_delivery_run_sheet": EtmsCatalogueListPageConfig(
        page_key="lcl_ftl_delivery_run_sheet",
        title="13.Delivery Run Sheet",
        page_hash="operation/lcl/delivery-run-sheet",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="operation_lcl_ftl",
        menu_parent_label="Operation",
    ),
}

MAINTENANCE_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "maintenance_quota": EtmsCatalogueListPageConfig(
        page_key="maintenance_quota",
        title="Maintenance quota",
        page_hash="maintenance/main-maintenance-quota",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="maintenance_and_repair",
        menu_parent_label="Maintenance and Repair",
    ),
    "maintenance_place": EtmsCatalogueListPageConfig(
        page_key="maintenance_place",
        title="Maintenance place",
        page_hash="maintenance/main-vehicle-maintenance-place",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="maintenance_and_repair",
        menu_parent_label="Maintenance and Repair",
    ),
    "vehicle_repair_level": EtmsCatalogueListPageConfig(
        page_key="vehicle_repair_level",
        title="Vehicle Repair Level",
        page_hash="maintenance/main-vehicle-repair-level",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="maintenance_and_repair",
        menu_parent_label="Maintenance and Repair",
    ),
}

MATERIAL_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "closing_material": EtmsCatalogueListPageConfig(
        page_key="closing_material",
        title="Closing material",
        page_hash="material/closing-material-management",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="material_management",
        menu_parent_label="Material Management",
    ),
}

ACCOUNTING_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "fuel_transaction": EtmsCatalogueListPageConfig(
        page_key="fuel_transaction",
        title="Fuel Transaction",
        page_hash="accounting/fuel-transaction",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "soa_list": EtmsCatalogueListPageConfig(
        page_key="soa_list",
        title="SOA list",
        page_hash="accounting/soa",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "drivers_allowance": EtmsCatalogueListPageConfig(
        page_key="drivers_allowance",
        title="Driver's Allowance",
        page_hash="accounting/salary-driver",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "unlock_trip_record": EtmsCatalogueListPageConfig(
        page_key="unlock_trip_record",
        title="Unlock Trip Record",
        page_hash="customer/unlock-trip-record",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "accounting_parameters": EtmsCatalogueListPageConfig(
        page_key="accounting_parameters",
        title="Parameters",
        page_hash="accounting/sys-parameter",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "cost_revenue_allocation": EtmsCatalogueListPageConfig(
        page_key="cost_revenue_allocation",
        title="Cost / Revenue Allocation",
        page_hash="accounting/cost-revenue-allocation",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "driver_allowance_parameter": EtmsCatalogueListPageConfig(
        page_key="driver_allowance_parameter",
        title="Driver Allowance Parameter",
        page_hash="accounting/driver-allowance-parameter",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "monthly_fuel_settlement": EtmsCatalogueListPageConfig(
        page_key="monthly_fuel_settlement",
        title="Monthly Fuel Settlement",
        page_hash="accounting/monthly-fuel-settlement",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "partner_debit": EtmsCatalogueListPageConfig(
        page_key="partner_debit",
        title="Partner Debit",
        page_hash="accounting/partner-debit",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "fuel_payment_request": EtmsCatalogueListPageConfig(
        page_key="fuel_payment_request",
        title="Fuel Payment Request",
        page_hash="accounting/fuel-payment-request",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "unlock_surcharge_request": EtmsCatalogueListPageConfig(
        page_key="unlock_surcharge_request",
        title="Unlock Surcharge Request",
        page_hash="accounting/unlock-surcharge",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "cod_clearing": EtmsCatalogueListPageConfig(
        page_key="cod_clearing",
        title="COD Clearing",
        page_hash="accounting/cod-clearing",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
    "accounting_receipts": EtmsCatalogueListPageConfig(
        page_key="accounting_receipts",
        title="Receipts",
        page_hash="accounting/receipt",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="accounting",
        menu_parent_label="Accounting",
    ),
}

SYSTEM_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    "user_info": EtmsCatalogueListPageConfig(
        page_key="user_info",
        title="User Info",
        page_hash="system/user-infor",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="system",
        menu_parent_label="System",
    ),
    "employee": EtmsCatalogueListPageConfig(
        page_key="employee",
        title="Employee",
        page_hash="system/employee",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="system",
        menu_parent_label="System",
    ),
    "permission": EtmsCatalogueListPageConfig(
        page_key="permission",
        title="Permission",
        page_hash="system/permission-list",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="system",
        menu_parent_label="System",
    ),
    "permission_instruction": EtmsCatalogueListPageConfig(
        page_key="permission_instruction",
        title="Permission Instruction",
        page_hash="system/permission-instruction",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="system",
        menu_parent_label="System",
    ),
    "menu": EtmsCatalogueListPageConfig(
        page_key="menu",
        title="Menu",
        page_hash="system/menu",
        menu_li_id="",
        list_column_headers=(),
        catalogue_suite="system",
        menu_parent_label="System",
    ),
}

CATALOGUE_LIST_PAGE_CONFIGS: dict[str, EtmsCatalogueListPageConfig] = {
    **TRANSPORT_NETWORK_LIST_PAGE_CONFIGS,
    **PARTNER_LIST_PAGE_CONFIGS,
    **VEHICLE_LIST_PAGE_CONFIGS,
    **DRIVER_LIST_PAGE_CONFIGS,
    **COMMODITY_LIST_PAGE_CONFIGS,
    **CATALOGUE_MASTER_LIST_PAGE_CONFIGS,
    **CUSTOMER_SERVICE_LIST_PAGE_CONFIGS,
    **OPERATION_LIST_PAGE_CONFIGS,
    **MAINTENANCE_LIST_PAGE_CONFIGS,
    **MATERIAL_LIST_PAGE_CONFIGS,
    **ACCOUNTING_LIST_PAGE_CONFIGS,
    **SYSTEM_LIST_PAGE_CONFIGS,
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
        elif self._config.catalogue_suite == "customer_service_common":
            self.open_customer_service_common_menu()
        elif self._config.catalogue_suite == "customer_service_fcl":
            self.open_customer_service_fcl_menu()
        elif self._config.catalogue_suite == "customer_service_lcl_ftl":
            self.open_customer_service_lcl_ftl_menu()
        elif self._config.catalogue_suite == "operation_common":
            self.open_operation_common_menu()
        elif self._config.catalogue_suite == "operation_fcl":
            self.open_operation_fcl_menu()
        elif self._config.catalogue_suite == "operation_lcl_ftl":
            self.open_operation_lcl_ftl_menu()
        elif self._config.catalogue_suite == "maintenance_and_repair":
            self.open_maintenance_and_repair_menu()
        elif self._config.catalogue_suite == "material_management":
            self.open_material_management_menu()
        elif self._config.catalogue_suite == "accounting":
            self.open_accounting_menu()
        elif self._config.catalogue_suite == "system":
            self.open_system_menu()
        else:
            self.open_transport_network_menu()

    def _menu_selectors(self) -> list[str]:
        title = self._config.title
        menu_li_id = self._config.menu_li_id
        page_hash = self._config.page_hash
        selectors: list[str] = []
        if menu_li_id:
            selectors.extend(
                [
                    f"#{menu_li_id} > a.nav-link",
                    (
                        f"xpath=//li[@id='{menu_li_id}']"
                        f"//span[normalize-space()='{title}']"
                        "/ancestor::a[contains(@class,'nav-link')][1]"
                    ),
                ]
            )
        if self._config.menu_parent_label:
            selectors.append(
                _sidebar_child_link(self._config.menu_parent_label, title)
            )
        selectors.extend(
            [
                _catalogue_submenu_link_by_label(title),
                (
                    "xpath=//a[contains(@class,'nav-link')]"
                    f"[.//span[normalize-space()='{title}']]"
                ),
                _sidebar_link_by_href(page_hash),
            ]
        )
        return list(dict.fromkeys(selectors))

    def _list_title_selectors(self) -> list[str]:
        title = self._config.title
        if self.page_key == "drivers_allowance":
            return [
                "xpath=//*[contains(@class,'page-title') and contains(normalize-space(),'Allowance')]",
                "xpath=//h5[contains(normalize-space(),'Allowance')]",
                *etms_page_title_selectors(title),
            ]
        return etms_page_title_selectors(title)

    _GENERIC_GRID_PAGE_KEYS = frozenset(
        {
            "verifying_booking",
            "fcl_surcharge_behalf",
            "fcl_surcharge_behalf_fleet",
            "lcl_ftl_transport_surcharge",
            "lcl_ftl_surcharge_behalf",
            "lcl_ftl_surcharge_behalf_fleet",
            "update_transport_info",
            "dispatching",
            "trip_settlement",
            "fuel_closing",
            "fcl_transport_request_list",
            "lcl_ftl_transport_request_list",
            "lcl_ftl_pickup_run_sheet",
            "lcl_ftl_revenue_protection",
            "lcl_ftl_routing",
            "lcl_ftl_consolidation",
            "lcl_ftl_transit",
            "lcl_ftl_delivery_run_sheet",
            "maintenance_quota",
            "maintenance_place",
            "vehicle_repair_level",
            "closing_material",
            "fuel_transaction",
            "soa_list",
            "drivers_allowance",
            "unlock_trip_record",
            "accounting_parameters",
            "cost_revenue_allocation",
            "driver_allowance_parameter",
            "monthly_fuel_settlement",
            "partner_debit",
            "fuel_payment_request",
            "unlock_surcharge_request",
            "cod_clearing",
            "accounting_receipts",
            "user_info",
            "employee",
            "permission",
            "permission_instruction",
            "menu",
        }
    )

    def _list_table_selectors(self) -> list[str]:
        title = self._config.title
        if self.page_key in self._GENERIC_GRID_PAGE_KEYS:
            portlet = (
                f"//*[contains(@class,'page-title') and contains(normalize-space(),'{title}')]"
                "/ancestor::div[contains(@class,'m-portlet') or contains(@class,'portlet')][1]"
            )
            return [
                f"xpath={portlet}//ngx-datatable//datatable-header-cell",
                f"xpath={portlet}//table//th",
                "xpath=//div[contains(@class,'m-portlet__body')]//ngx-datatable//datatable-header-cell",
                "xpath=//div[contains(@class,'m-portlet__body')]//table//th",
                "xpath=//ngx-datatable//datatable-header-cell",
            ]
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
        self._wait_for_list_grid(min_rows, allow_no_data=allow_no_data)
        return self

    def _wait_for_list_grid(self, min_rows: int, *, allow_no_data: bool = False) -> None:
        self.wait_for_visible(
            self._list_title_selectors(),
            f"{self._config.title} page title",
        )
        if self.page_key in self._GENERIC_GRID_PAGE_KEYS:
            self.wait_for_page_stable()
            if allow_no_data:
                self.list_grid.wait_for_data_rows_or_no_data(
                    min_rows=min_rows,
                    table_selectors=None,
                )
            else:
                self.list_grid.wait_for_data_rows(
                    min_rows=min_rows,
                    table_selectors=None,
                )
            return
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
        first_page_step: bool = False,
    ) -> str:
        """Submenu is opened by the performance suite — timed step is sidebar click → data."""
        del tab_key, min_rows, allow_no_data, first_page_step
        return "page_load"

    def run_performance_measurement(
        self,
        *,
        tab_key: str | None = None,
        min_rows: int = 1,
        allow_no_data: bool = False,
        mode: str = "page_load",
    ) -> None:
        """Timed segment: sidebar menu click → list grid data displayed."""
        del tab_key
        if mode == "skipped":
            return
        self._click_sidebar_link(
            self._menu_selectors(),
            f"{self._config.title} menu",
        )
        self._wait_for_url_hash(self.page_hash)
        self.wait_for_page_stable()
        self._wait_for_list_grid(min_rows, allow_no_data=allow_no_data)

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
