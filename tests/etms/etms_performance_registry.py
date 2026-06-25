"""eTMS performance test — page registry and post-load verification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from automation.logging.step_logger import record_step_log
from automation.pages.etms.etms_catalogue_list_page import (
    CATALOGUE_LIST_PAGE_CONFIGS,
    PARTNER_LIST_PAGE_CONFIGS,
    TRANSPORT_NETWORK_LIST_PAGE_CONFIGS,
)
from automation.pages.page_manager import PageManager

_DEDICATED_PERF_PAGES: dict[str, str] = {
    "administrative_units": "Administrative Units Page",
    "zone_code": "Zone Code Page",
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

    raise KeyError(f"No PageManager resolver for performance page_key '{page_key}'")


def verify_performance_page_loaded(
    *,
    check_label: str,
    page: Any,
    min_rows: int,
    tab_key: str | None = None,
) -> int:
    """Assert URL hash + scoped table data rows after a performance step."""
    if tab_key and hasattr(page, "list_table_selectors_for_tab"):
        table_selectors = page.list_table_selectors_for_tab(tab_key)
    else:
        table_selectors = page.list_table_selectors

    actual_rows = page.list_grid.count_data_rows(table_selectors=table_selectors)
    assert actual_rows >= min_rows, (
        f"{check_label}: table must display at least {min_rows} data row(s), "
        f"got {actual_rows}"
    )

    page_hash = page.page_hash
    normalized_url = page.current_url.lower().replace("_", "-")
    assert page_hash in normalized_url, (
        f"{check_label} URL hash '{page_hash}' not found after navigation"
    )

    record_step_log(
        f"[PERF VERIFY] {check_label}: url OK, "
        f"table_data_rows={actual_rows} (min={min_rows})"
    )
    return actual_rows


# Backward-compatible re-exports
__all__ = [
    "CATALOGUE_LIST_PAGE_CONFIGS",
    "PARTNER_LIST_PAGE_CONFIGS",
    "PERFORMANCE_PAGE_TARGETS",
    "TRANSPORT_NETWORK_LIST_PAGE_CONFIGS",
    "EtmsPerformancePageTarget",
    "build_performance_page_targets",
    "resolve_performance_page",
    "verify_performance_page_loaded",
]
