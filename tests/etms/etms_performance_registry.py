"""eTMS performance test — page registry and post-load verification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from automation.logging.step_logger import record_step_log
from automation.pages.etms.etms_catalogue_list_page import (
    CATALOGUE_LIST_PAGE_CONFIGS,
    PARTNER_LIST_PAGE_CONFIGS,
    TRANSPORT_NETWORK_LIST_PAGE_CONFIGS,
    VEHICLE_LIST_PAGE_CONFIGS,
    DRIVER_LIST_PAGE_CONFIGS,
    COMMODITY_LIST_PAGE_CONFIGS,
    CATALOGUE_MASTER_LIST_PAGE_CONFIGS,
)
from automation.pages.page_manager import PageManager

_DEDICATED_PERF_PAGES: dict[str, str] = {
    "administrative_units": "Administrative Units Page",
    "zone_code": "Zone Code Page",
    "booking_information": "Booking Information Page",
    "vehicle_part_type": "Vehicle Part Type Page",
    "vehicle_type": "Vehicle Type Page",
    "cost_of_route": "Cost Of Route Page",
    "price_toll_buying": "Price Toll Buying Page",
    "fcl_rate_card_list": "FCL Rate Card List Page",
    "fcl_buying_price": "FCL Buying Price Page",
    "fcl_renting_container": "Renting Container FCL Page",
    "fcl_renting_vehicle": "Renting vehicle Page",
    "lcl_rate_card": "3. LCL Rate Card Page",
    "lcl_buying": "LCL Buying Page",
    "distribution_rate_card": "2. Distribution Rate Card Page",
    "distribution_buying": "Distribution Buying Page",
    "pricing_report": "Pricing Report Page",
    "commission_rate_card": "Commission Rate Card Page",
    "create_fcl_quotation": "Create FCL Quotation Page",
    "fcl_quotation_list": "FCL Quotation List Page",
    "create_lcl_quotation": "Create LCL Quotation Page",
    "create_distribution_quotation": "Create Distribution Quotation Page",
    "fcl_booking": "FCL Booking Page",
    "fcl_surcharge_behalf": "FCL Surcharge/ Behalf Page",
    "container_deposit_management": "Container Deposit Management Page",
    "fcl_surcharge_behalf_fleet": "FCL Surcharge/ Behalf (Fleet) Page",
    "lcl_ftl_booking": "LCL/FTL Booking Page",
    "lcl_ftl_transport_surcharge": "LCL/FTL Transport Surcharge Page",
    "lcl_ftl_surcharge_behalf": "LCL/FTL Surcharge/Behalf Page",
    "lcl_shipment_management": "LCL Shipment Management Page",
    "lcl_ftl_surcharge_behalf_fleet": "LCL/FTL Surcharge/ Behalf (Fleet) Page",
    "soa_for_outsource": "SOA For Outsource Page",
}


@dataclass(frozen=True)
class EtmsPerformancePageTarget:
    page_key: str
    check_label: str


def build_performance_page_targets() -> dict[str, EtmsPerformancePageTarget]:
    """Build registry from dedicated pages + catalogue list config dicts."""
    targets = {
        page_key: EtmsPerformancePageTarget(page_key, check_label)
        for page_key, check_label in _DEDICATED_PERF_PAGES.items()
    }
    for page_key, config in CATALOGUE_LIST_PAGE_CONFIGS.items():
        targets[page_key] = EtmsPerformancePageTarget(
            page_key=page_key,
            check_label=f"{config.title} Page",
        )
    return targets


PERFORMANCE_PAGE_TARGETS: dict[str, EtmsPerformancePageTarget] = build_performance_page_targets()


def resolve_performance_page(pages: PageManager, page_key: str) -> Any:
    """Return the Page Object for a configured performance page_key."""
    if page_key not in PERFORMANCE_PAGE_TARGETS:
        known = ", ".join(sorted(PERFORMANCE_PAGE_TARGETS))
        raise KeyError(f"Unknown performance page_key '{page_key}'. Known: {known}")

    if page_key in CATALOGUE_LIST_PAGE_CONFIGS:
        return pages.etms_catalogue_list_page(page_key)
    if page_key == "administrative_units":
        return pages.etms_administrative_units_page
    if page_key == "zone_code":
        return pages.etms_zone_code_page
    if page_key == "booking_information":
        return pages.etms_booking_information_page
    if page_key == "vehicle_part_type":
        return pages.etms_vehicle_part_type_page
    if page_key == "vehicle_type":
        return pages.etms_vehicle_type_page
    if page_key == "cost_of_route":
        return pages.etms_cost_of_route_workflow_page
    if page_key == "price_toll_buying":
        return pages.etms_price_toll_buying_page
    if page_key == "fcl_rate_card_list":
        return pages.etms_fcl_rate_card_list_page
    if page_key == "fcl_buying_price":
        return pages.etms_fcl_buying_price_page
    if page_key == "fcl_renting_container":
        return pages.etms_fcl_renting_container_page
    if page_key == "fcl_renting_vehicle":
        return pages.etms_fcl_renting_vehicle_page
    if page_key == "lcl_rate_card":
        return pages.etms_lcl_rate_card_page
    if page_key == "lcl_buying":
        return pages.etms_lcl_buying_page
    if page_key == "distribution_rate_card":
        return pages.etms_distribution_rate_card_page
    if page_key == "distribution_buying":
        return pages.etms_distribution_buying_page
    if page_key == "pricing_report":
        return pages.etms_pricing_report_page
    if page_key == "commission_rate_card":
        return pages.etms_commission_rate_card_page
    if page_key == "create_fcl_quotation":
        return pages.etms_create_fcl_quotation_page
    if page_key == "fcl_quotation_list":
        return pages.etms_fcl_quotation_list_page
    if page_key == "create_lcl_quotation":
        return pages.etms_create_lcl_quotation_page
    if page_key == "create_distribution_quotation":
        return pages.etms_create_distribution_quotation_page
    if page_key == "fcl_booking":
        return pages.etms_fcl_booking_page
    if page_key == "container_deposit_management":
        return pages.etms_container_deposit_management_page
    if page_key == "lcl_ftl_booking":
        return pages.etms_lcl_ftl_booking_page
    if page_key == "lcl_shipment_management":
        return pages.etms_lcl_shipment_management_page
    if page_key == "soa_for_outsource":
        return pages.etms_soa_for_outsource_page

    raise KeyError(f"No PageManager resolver for performance page_key '{page_key}'")


def verify_performance_page_loaded(
    *,
    check_label: str,
    page: Any,
    min_rows: int,
    tab_key: str | None = None,
    allow_no_data: bool = False,
    optional_tab: bool = False,
) -> int:
    """Assert URL hash + scoped table data rows (or 'No Data' empty state) after a performance step."""
    if optional_tab and tab_key and hasattr(page, "optional_tab_keys"):
        if tab_key in page.optional_tab_keys and not page._is_tab_available(tab_key):
            normalized_url = page.current_url.lower().replace("_", "-")
            assert page.page_hash in normalized_url, (
                f"{check_label} URL hash '{page.page_hash}' not found"
            )
            record_step_log(
                f"[PERF VERIFY] {check_label}: optional tab not on page — skipped (url OK)"
            )
            return 0

    if hasattr(page, "verify_performance_step"):
        page.verify_performance_step(
            check_label=check_label,
            tab_key=tab_key,
            min_rows=min_rows,
            allow_no_data=allow_no_data,
        )
        return 0

    settle_performance_page(
        page,
        min_rows=min_rows,
        tab_key=tab_key,
        allow_no_data=allow_no_data,
    )
    actual_rows = _count_performance_table_rows(page, tab_key=tab_key)
    no_data = _has_no_data_display(page, tab_key=tab_key)

    if allow_no_data and actual_rows == 0 and no_data:
        record_step_log(
            f"[PERF VERIFY] {check_label}: url OK, empty state 'No Data' displayed"
        )
    else:
        assert actual_rows >= min_rows, (
            f"{check_label}: table must display at least {min_rows} data row(s), "
            f"got {actual_rows}"
        )
        record_step_log(
            f"[PERF VERIFY] {check_label}: url OK, "
            f"table_data_rows={actual_rows} (min={min_rows})"
        )

    page_hash = page.page_hash
    if tab_key and hasattr(page, "page_hash_for_tab"):
        page_hash = page.page_hash_for_tab(tab_key)
    normalized_url = page.current_url.lower().replace("_", "-")
    assert page_hash in normalized_url, (
        f"{check_label} URL hash '{page_hash}' not found after navigation"
    )

    return actual_rows


def _has_no_data_display(page: Any, *, tab_key: str | None) -> bool:
    if tab_key and hasattr(page, "has_no_data_for_tab"):
        return page.has_no_data_for_tab(tab_key)
    if hasattr(page, "list_grid"):
        table_selectors = None
        if tab_key and hasattr(page, "list_table_selectors_for_tab"):
            table_selectors = page.list_table_selectors_for_tab(tab_key)
        return page.list_grid.is_no_data_displayed(table_selectors=table_selectors)
    return False


def _count_performance_table_rows(page: Any, *, tab_key: str | None) -> int:
    if tab_key and hasattr(page, "count_data_rows_for_tab"):
        return page.count_data_rows_for_tab(tab_key)
    if tab_key and hasattr(page, "list_table_selectors_for_tab"):
        table_selectors = page.list_table_selectors_for_tab(tab_key)
        return page.list_grid.count_data_rows(table_selectors=table_selectors)
    return page.list_grid.count_data_rows(table_selectors=page.list_table_selectors)


def settle_performance_page(
    page: Any,
    *,
    min_rows: int,
    tab_key: str | None = None,
    allow_no_data: bool = False,
) -> None:
    """Wait for overlays to clear and re-verify grid before the next navigation."""
    if hasattr(page, "confirm_grid_loaded"):
        if tab_key is not None:
            page.confirm_grid_loaded(
                min_rows,
                tab_key=tab_key,
                allow_no_data=allow_no_data,
            )
        else:
            page.confirm_grid_loaded(min_rows, allow_no_data=allow_no_data)
        return
    if hasattr(page, "wait_before_next_catalogue_navigation"):
        page.wait_before_next_catalogue_navigation()


# Backward-compatible re-exports
__all__ = [
    "CATALOGUE_LIST_PAGE_CONFIGS",
    "PARTNER_LIST_PAGE_CONFIGS",
    "PERFORMANCE_PAGE_TARGETS",
    "TRANSPORT_NETWORK_LIST_PAGE_CONFIGS",
    "VEHICLE_LIST_PAGE_CONFIGS",
    "DRIVER_LIST_PAGE_CONFIGS",
    "COMMODITY_LIST_PAGE_CONFIGS",
    "CATALOGUE_MASTER_LIST_PAGE_CONFIGS",
    "EtmsPerformancePageTarget",
    "build_performance_page_targets",
    "resolve_performance_page",
    "settle_performance_page",
    "verify_performance_page_loaded",
]
