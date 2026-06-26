from __future__ import annotations

from collections.abc import Callable
from typing import Any

from automation.logging.step_logger import record_step_log
from automation.pages.page_manager import PageManager
from automation.performance import StepPerformanceTracker

from automation.pages.etms.etms_catalogue_menu_page import (
    _sidebar_child_link,
    _sidebar_link_by_href,
)
from tests.etms.etms_performance_registry import (
    PERFORMANCE_PAGE_TARGETS,
    resolve_performance_page,
    settle_performance_page,
    verify_performance_page_loaded,
)

_CATALOGUE_SUITE_NAVIGATORS: dict[str, Callable[[Any], None]] = {
    "transport_network": lambda nav_page: nav_page.open_transport_network_menu(),
    "partner": lambda nav_page: nav_page.open_partner_menu(),
    "vehicle": lambda nav_page: nav_page.open_vehicle_menu(),
    "driver": lambda nav_page: nav_page.open_driver_menu(),
    "commodity": lambda nav_page: nav_page.open_commodity_menu(),
    "catalogue_master": lambda nav_page: nav_page.open_catalogue_menu(),
}

_DIRECT_SUITE_MENU_OPENERS: dict[str, Callable[[Any], None]] = {
    "pricing_common": lambda nav_page: nav_page.open_pricing_common_menu(),
    "pricing_fcl": lambda nav_page: nav_page.open_pricing_fcl_menu(),
    "pricing_lcl": lambda nav_page: nav_page.open_pricing_lcl_menu(),
    "pricing_distribution": lambda nav_page: nav_page.open_pricing_distribution_menu(),
    "pricing_report": lambda nav_page: nav_page.open_pricing_report_menu(),
    "quotation": lambda nav_page: nav_page.open_quotation_menu(),
    "customer_service_common": lambda nav_page: nav_page.open_customer_service_common_menu(),
    "customer_service_fcl": lambda nav_page: nav_page.open_customer_service_fcl_menu(),
    "customer_service_lcl_ftl": lambda nav_page: nav_page.open_customer_service_lcl_ftl_menu(),
    "customer_service_soa_outsource": lambda nav_page: nav_page.open_customer_service_soa_outsource_menu(),
    "operation_common": lambda nav_page: nav_page.open_operation_common_menu(),
    "operation_fcl": lambda nav_page: nav_page.open_operation_fcl_menu(),
    "operation_lcl_ftl": lambda nav_page: nav_page.open_operation_lcl_ftl_menu(),
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


def _open_performance_suite_menu(nav_page: Any, suite: str) -> None:
    opener = _DIRECT_SUITE_MENU_OPENERS.get(suite)
    if opener is not None:
        opener(nav_page)
        return
    _open_catalogue_submenu(nav_page, suite)


def _load_performance_page(
    page: Any,
    *,
    min_rows: int,
    tab_key: str | None,
    allow_no_data: bool = False,
    perf_mode: str | None = None,
) -> None:
    if perf_mode is not None and hasattr(page, "run_performance_measurement"):
        page.run_performance_measurement(
            tab_key=tab_key,
            min_rows=min_rows,
            allow_no_data=allow_no_data,
            mode=perf_mode,
        )
        return
    if tab_key is not None:
        try:
            page.load_page_for_performance(
                min_rows=min_rows,
                tab_key=tab_key,
                allow_no_data=allow_no_data,
            )
        except TypeError:
            page.load_page_for_performance(min_rows=min_rows, tab_key=tab_key)
    else:
        page.load_page_for_performance(min_rows=min_rows)


def _is_sidebar_page_available(page: Any) -> bool:
    config = getattr(page, "_config", None)
    if config is not None and getattr(config, "menu_parent_label", ""):
        scoped = [
            _sidebar_child_link(config.menu_parent_label, config.title),
            _sidebar_link_by_href(config.page_hash),
        ]
        return page.find_visible(scoped) is not None
    if hasattr(page, "_menu_selectors"):
        return page.find_visible(page._menu_selectors()) is not None
    return True


def run_etms_catalogue_performance_suite(
    *,
    pages: PageManager,
    data: dict[str, Any],
    login_etms: Callable[[str], None],
) -> None:
    """Login once, open suite submenu, measure each configured page, assert thresholds."""
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

    prev_page: Any | None = None
    prev_tab_key: str | None = None
    prev_min_rows = default_min_rows
    prev_allow_no_data = False

    for index, page_config in enumerate(page_configs):
        page_key = str(page_config["page_key"])
        target = PERFORMANCE_PAGE_TARGETS[page_key]
        check_label = str(page_config.get("check_label", target.check_label))
        threshold_seconds = _resolve_page_threshold(page_config)
        min_rows = int(page_config.get("min_table_rows", default_min_rows))
        allow_no_data = bool(
            page_config.get("allow_no_data", data.get("allow_no_data", False))
        )
        tab_key = page_config.get("tab")
        tab_key = str(tab_key) if tab_key else None
        page = resolve_performance_page(pages, page_key)

        if index > 0 and prev_page is not None:
            same_page = page_key == str(page_configs[index - 1].get("page_key"))
            if same_page and hasattr(prev_page, "wait_before_next_pricing_navigation"):
                prev_page.wait_before_next_pricing_navigation()
            else:
                settle_performance_page(
                    prev_page,
                    min_rows=prev_min_rows,
                    tab_key=prev_tab_key,
                    allow_no_data=prev_allow_no_data,
                )
                if hasattr(prev_page, "wait_before_next_pricing_navigation"):
                    prev_page.wait_before_next_pricing_navigation()
                else:
                    nav_page.wait_before_next_catalogue_navigation()

        _open_performance_suite_menu(nav_page, suite)

        optional_page = bool(page_config.get("optional_page"))
        if optional_page and not _is_sidebar_page_available(page):
            record_step_log(
                f"[PERF SKIP] {check_label}: optional page not in sidebar menu"
            )
            continue

        perf_mode: str | None = None
        first_page_step = (
            index == 0
            or page_key != str(page_configs[index - 1].get("page_key"))
        )
        if hasattr(page, "prepare_for_performance"):
            try:
                perf_mode = page.prepare_for_performance(
                    tab_key=tab_key,
                    min_rows=min_rows,
                    allow_no_data=allow_no_data,
                    first_page_step=first_page_step,
                )
            except TypeError:
                perf_mode = page.prepare_for_performance(
                    tab_key=tab_key,
                    min_rows=min_rows,
                    allow_no_data=allow_no_data,
                )

        tracker.run_step(
            check_label,
            lambda current_page=page, rows=min_rows, tab=tab_key, empty=allow_no_data, mode=perf_mode: _load_performance_page(
                current_page,
                min_rows=rows,
                tab_key=tab,
                allow_no_data=empty,
                perf_mode=mode,
            ),
            threshold_seconds=threshold_seconds,
        )

        verify_performance_page_loaded(
            check_label=check_label,
            page=page,
            min_rows=min_rows,
            tab_key=tab_key,
            allow_no_data=allow_no_data,
            optional_tab=bool(page_config.get("optional_tab")),
        )

        prev_page = page
        prev_tab_key = tab_key
        prev_min_rows = min_rows
        prev_allow_no_data = allow_no_data

    tracker.assert_all_within_threshold()


def run_etms_performance_suite(
    *,
    suite: str,
    pages: PageManager,
    data: dict[str, Any],
    login_etms: Callable[[str], None],
    use_setdefault: bool = False,
) -> None:
    """Run a named performance suite — injects ``suite`` into payload then delegates."""
    payload = dict(data)
    if use_setdefault:
        payload.setdefault("suite", suite)
    else:
        payload["suite"] = suite
    run_etms_catalogue_performance_suite(
        pages=pages,
        data=payload,
        login_etms=login_etms,
    )
