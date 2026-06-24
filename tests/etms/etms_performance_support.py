from __future__ import annotations

from collections.abc import Callable
from typing import Any

from automation.logging.step_logger import record_step_log
from automation.pages.page_manager import PageManager
from automation.performance import StepPerformanceTracker

from tests.etms.etms_performance_registry import (
    PERFORMANCE_PAGE_TARGETS,
    resolve_performance_page,
    verify_performance_page_loaded,
)


def _resolve_page_threshold(page_config: dict[str, Any]) -> float:
    if "max_step_seconds" not in page_config:
        page_key = page_config.get("page_key", "?")
        raise AssertionError(
            f"Performance page '{page_key}' must define 'max_step_seconds'"
        )
    return float(page_config["max_step_seconds"])


def run_etms_transport_network_performance_suite(
    *,
    pages: PageManager,
    data: dict[str, Any],
    login_etms: Callable[[str], None],
) -> None:
    """Login once, measure each configured page, then compare all results to thresholds."""
    branch = str(data["branch"])
    default_min_rows = int(data.get("min_table_rows", 1))
    page_configs = data.get("pages", [])

    if not page_configs:
        raise AssertionError("Performance test data must include at least one page in 'pages'")

    login_etms(branch)

    nav_page = pages.etms_places_page
    tracker = StepPerformanceTracker()

    threshold_summary = ", ".join(
        f"{cfg.get('page_key')}={cfg['max_step_seconds']}s"
        for cfg in page_configs
        if "max_step_seconds" in cfg
    )
    record_step_log(
        f"[PERF CONFIG] branch={branch}, min_table_rows={default_min_rows}, "
        f"pages={len(page_configs)}, thresholds=[{threshold_summary}]"
    )

    for page_config in page_configs:
        page_key = str(page_config["page_key"])
        target = PERFORMANCE_PAGE_TARGETS[page_key]
        check_label = str(page_config.get("check_label", target.check_label))
        threshold_seconds = _resolve_page_threshold(page_config)
        min_rows = int(page_config.get("min_table_rows", default_min_rows))
        page = resolve_performance_page(pages, page_key)

        nav_page.open_catalogue_menu()
        nav_page.open_transport_network_menu()

        tracker.run_step(
            check_label,
            lambda current_page=page, rows=min_rows: current_page.load_page_for_performance(
                min_rows=rows
            ),
            threshold_seconds=threshold_seconds,
        )

        verify_performance_page_loaded(
            check_label=check_label,
            page=page,
            min_rows=min_rows,
        )

    tracker.assert_all_within_threshold()
