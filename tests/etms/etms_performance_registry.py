"""eTMS performance test — page registry and post-load verification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from automation.logging.step_logger import record_step_log
from automation.pages.etms.etms_transport_network_list_page import (
    TRANSPORT_NETWORK_LIST_PAGE_CONFIGS,
)
from automation.pages.page_manager import PageManager

_DEDICATED_PERF_PAGES: dict[str, str] = {
    "places": "Places Page",
    "distance_between_places": "Distance Between Places Page",
}


@dataclass(frozen=True)
class EtmsPerformancePageTarget:
    page_key: str
    check_label: str


def build_performance_page_targets() -> dict[str, EtmsPerformancePageTarget]:
    """Build registry from dedicated pages + Transport Network config dict."""
    targets = {
        page_key: EtmsPerformancePageTarget(page_key, check_label)
        for page_key, check_label in _DEDICATED_PERF_PAGES.items()
    }
    for page_key, config in TRANSPORT_NETWORK_LIST_PAGE_CONFIGS.items():
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

    if page_key in TRANSPORT_NETWORK_LIST_PAGE_CONFIGS:
        return pages.etms_transport_network_list_page(page_key)
    if page_key == "places":
        return pages.etms_places_page
    if page_key == "distance_between_places":
        return pages.etms_distance_between_places_page

    raise KeyError(f"No PageManager resolver for performance page_key '{page_key}'")


def verify_performance_page_loaded(
    *,
    check_label: str,
    page: Any,
    min_rows: int,
) -> int:
    """Assert URL hash + scoped table data rows after a performance step."""
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
