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

_CATALOGUE_SUITE_NAVIGATORS: dict[str, Callable[[Any], None]] = {
    "transport_network": lambda nav_page: nav_page.open_transport_network_menu(),
    "partner": lambda nav_page: nav_page.open_partner_menu(),
}


def _resolve_page_threshold(page_config: dict[str, Any]) -> float:
    if "max_step_seconds" not in page_config:
        page_key = page_config.get("page_key", "?")
        raise AssertionError(
            f"Performance page '{page_key}' must define 'max_step_seconds'"
        )
    return float(page_config["max_step_seconds"])


def _open_catalogue_submenu(nav_page: Any, suite: str) -> None:
    nav_page.open_catalogue_menu()
    opener = _CATALOGUE_SUITE_NAVIGATORS.get(suite)
    if opener is None:
        known = ", ".join(sorted(_CATALOGUE_SUITE_NAVIGATORS))
        raise AssertionError(
            f"Unknown performance suite '{suite}'. Known catalogue suites: {known}"
        )
    opener(nav_page)


def _load_performance_page(page: Any, *, min_rows: int, tab_key: str | None) -> None:
    if tab_key is not None:
        page.load_page_for_performance(min_rows=min_rows, tab_key=tab_key)
    else:
        page.load_page_for_performance(min_rows=min_rows)


def run_etms_catalogue_performance_suite(
    *,
    pages: PageManager,
    data: dict[str, Any],
    login_etms: Callable[[str], None],
) -> None:
    """Login once, open catalogue submenu, measure each configured page, assert thresholds."""
    branch = str(data["branch"])
    suite = str(data.get("suite", "transport_network"))
    default_min_rows = int(data.get("min_table_rows", 1))
    page_configs = data.get("pages", [])

    if not page_configs:
        raise AssertionError("Performance test data must include at least one page in 'pages'")

    login_etms(branch)

    nav_page = pages.etms_catalogue_menu_page
    tracker = StepPerformanceTracker()

    threshold_summary = ", ".join(
        f"{cfg.get('page_key')}={cfg['max_step_seconds']}s"
        for cfg in page_configs
        if "max_step_seconds" in cfg
    )
    record_step_log(
        f"[PERF CONFIG] suite={suite}, branch={branch}, min_table_rows={default_min_rows}, "
        f"pages={len(page_configs)}, thresholds=[{threshold_summary}]"
    )

    for page_config in page_configs:
        page_key = str(page_config["page_key"])
        target = PERFORMANCE_PAGE_TARGETS[page_key]
        check_label = str(page_config.get("check_label", target.check_label))
        threshold_seconds = _resolve_page_threshold(page_config)
        min_rows = int(page_config.get("min_table_rows", default_min_rows))
        tab_key = page_config.get("tab")
        tab_key = str(tab_key) if tab_key else None
        page = resolve_performance_page(pages, page_key)

        _open_catalogue_submenu(nav_page, suite)

        tracker.run_step(
            check_label,
            lambda current_page=page, rows=min_rows, tab=tab_key: _load_performance_page(
                current_page,
                min_rows=rows,
                tab_key=tab,
            ),
            threshold_seconds=threshold_seconds,
        )

        verify_performance_page_loaded(
            check_label=check_label,
            page=page,
            min_rows=min_rows,
            tab_key=tab_key,
        )

    tracker.assert_all_within_threshold()


def run_etms_transport_network_performance_suite(
    *,
    pages: PageManager,
    data: dict[str, Any],
    login_etms: Callable[[str], None],
) -> None:
    """Backward-compatible wrapper for PERF_TN_001."""
    payload = dict(data)
    payload.setdefault("suite", "transport_network")
    run_etms_catalogue_performance_suite(
        pages=pages,
        data=payload,
        login_etms=login_etms,
    )


def run_etms_partner_performance_suite(
    *,
    pages: PageManager,
    data: dict[str, Any],
    login_etms: Callable[[str], None],
) -> None:
    """Catalogue > Partner performance suite (PERF_PT_001)."""
    payload = dict(data)
    payload["suite"] = "partner"
    run_etms_catalogue_performance_suite(
        pages=pages,
        data=payload,
        login_etms=login_etms,
    )
