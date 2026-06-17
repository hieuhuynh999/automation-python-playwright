from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any, cast

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright
from pytest_html import extras
from pytest_metadata.plugin import metadata_key

from automation.config import get_settings, settings
from automation.logging import get_step_logs, logger, reset_step_logs, safe_terminal_print
from automation.pages import PageManager
from automation.reporting.reportportal_support import (
    attach_failure_screenshot,
    attach_text_artifact,
    get_rp_logger,
    is_reportportal_enabled,
    log_step_lines,
    resolve_test_display_name,
)

pytest_plugins = ["tests.conftest_reportportal"]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--browser", choices=["chrome", "edge"], default=None)
    parser.addoption("--browser-headless", choices=["true", "false"], default=None)


def pytest_configure(config: pytest.Config) -> None:
    Path("reports").mkdir(exist_ok=True)
    Path(settings.screenshot_dir).mkdir(parents=True, exist_ok=True)

    browser_name = config.getoption("--browser") or settings.browser

    headless_option = config.getoption("--browser-headless")

    headless = (
        settings.browser_headless if headless_option is None else headless_option.lower() == "true"
    )

    metadata = config.stash[metadata_key]

    metadata.pop("Python", None)
    metadata.pop("Platform", None)
    metadata.pop("Packages", None)
    metadata.pop("Plugins", None)

    metadata["Environment"] = settings.env
    metadata["Browser"] = browser_name
    metadata["Headless"] = str(headless)
    metadata["Timeout"] = str(settings.browser_timeout)
    metadata["Base URL"] = settings.efms_base_url


def pytest_sessionstart(session: pytest.Session) -> None:
    if is_reportportal_enabled(session.config):
        get_rp_logger()
        endpoint = str(session.config.getini("rp_endpoint")).rstrip("/")
        project = session.config.getini("rp_project")
        logger.info(
            "ReportPortal enabled: endpoint=%s project=%s",
            endpoint,
            project,
        )
        logger.info(
            "View launches: %s/ui/#%s/launches/all",
            endpoint,
            project,
        )


def pytest_html_report_title(report):
    report.title = "Automation Report"


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture()
def browser(
    pytestconfig: pytest.Config,
    playwright_instance: Playwright,
) -> Generator[Browser, None, None]:

    browser_name = (pytestconfig.getoption("--browser") or settings.browser).lower()

    headless_option = pytestconfig.getoption("--browser-headless")

    headless = (
        settings.browser_headless if headless_option is None else headless_option.lower() == "true"
    )

    browser_channels = {
        "chrome": "chrome",
        "edge": "msedge",
    }

    if browser_name not in browser_channels:
        raise ValueError(
            f"Unsupported browser: {browser_name}. "
            f"Supported browsers: {', '.join(browser_channels.keys())}"
        )

    logger.info(
        f"Launching browser={browser_name}, headless={headless}, slow_mo={settings.browser_slow_mo}"
    )

    browser = playwright_instance.chromium.launch(
        channel=browser_channels[browser_name],
        headless=headless,
        slow_mo=settings.browser_slow_mo,
        args=["--start-maximized"],
    )

    yield browser

    logger.info("Closing browser")

    browser.close()


def _is_headless(pytestconfig: pytest.Config) -> bool:
    headless_option = pytestconfig.getoption("--browser-headless")
    if headless_option is None:
        return settings.browser_headless
    return headless_option.lower() == "true"


@pytest.fixture()
def context(
    browser: Browser,
    pytestconfig: pytest.Config,
) -> Generator[BrowserContext, None, None]:
    if _is_headless(pytestconfig):
        context = browser.new_context(
            viewport={
                "width": settings.headless_viewport_width,
                "height": settings.headless_viewport_height,
            },
        )
    else:
        context = browser.new_context(
            viewport=None,
            no_viewport=True,
        )

    # Timeout cho element:
    # click, fill, locator, expect...
    context.set_default_timeout(settings.browser_timeout)

    # Timeout cho page navigation:
    # goto(), reload(), wait_for_url()
    context.set_default_navigation_timeout(settings.page_load_timeout)

    yield context

    context.close()


@pytest.fixture()
def page(context: BrowserContext) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page


@pytest.fixture()
def pages(page: Page) -> PageManager:
    return PageManager(page)


@pytest.fixture()
def efms_account_password() -> str:
    cfg = get_settings()
    password = cfg.efms_password or os.getenv("EFMS_ACCOUNT_PASSWORD")
    if not password:
        pytest.skip(
            "Set EFMS_ACCOUNT_PASSWORD (or legacy ACCOUNT_PASSWORD) to run eFMS login tests"
        )
    return password


@pytest.fixture()
def etms_account_password() -> str:
    cfg = get_settings()
    password = cfg.etms_password or os.getenv("ETMS_ACCOUNT_PASSWORD")
    if not password:
        pytest.skip("Set ETMS_ACCOUNT_PASSWORD to run eTMS login tests")
    return password


def _get_test_case_id(test_data: Any) -> str:
    if not isinstance(test_data, dict):
        return ""

    test_case_ids = test_data.get("test_case_ids")
    if isinstance(test_case_ids, list):
        return " | ".join(str(tc_id) for tc_id in test_case_ids if tc_id)

    if test_case_ids:
        return str(test_case_ids)

    test_case_id = test_data.get("test_case_id")
    return str(test_case_id) if test_case_id else ""


def _get_description(test_data: Any, default: str) -> str:
    if not isinstance(test_data, dict):
        return default

    description = test_data.get("description")
    return str(description) if description else default


def _get_scenario_lines(test_data: Any) -> list[str]:
    if not isinstance(test_data, dict):
        return []

    scenario_lines: list[str] = []
    for scenario in test_data.get("scenarios", []):
        if not isinstance(scenario, dict):
            continue

        tc_id = scenario.get("test_case_id")
        description = scenario.get("description")
        if tc_id and description:
            scenario_lines.append(f"- {tc_id}: {description}")
        elif tc_id:
            scenario_lines.append(f"- {tc_id}")

    return scenario_lines


def _get_test_case_ids_text(test_data: Any) -> str:
    if not isinstance(test_data, dict):
        return ""

    test_case_ids = test_data.get("test_case_ids")
    if isinstance(test_case_ids, list):
        return "\n".join(str(tc_id) for tc_id in test_case_ids if tc_id)

    return str(test_case_ids) if test_case_ids else ""


def pytest_runtest_setup(item: pytest.Item) -> None:
    del item
    reset_step_logs()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo,
):
    outcome = yield
    report = outcome.get_result()
    if report.when not in {"setup", "call"}:
        return

    if report.when == "setup" and report.passed:
        return

    # ==========================
    # Test Case Information
    # ==========================
    tc_id = ""
    description = item.name
    funcargs = getattr(item, "funcargs", {})

    # 1. Get from JSON data provider
    test_data = funcargs.get("data") if isinstance(funcargs, dict) else None
    if test_data:
        tc_id = _get_test_case_id(test_data)
        description = _get_description(test_data, item.name)

    # 2. Fallback get from pytest marker
    if not tc_id:
        tc_id_marker = item.get_closest_marker("tc_id")

        if tc_id_marker and tc_id_marker.args:
            tc_id = tc_id_marker.args[0]

    if description == item.name:
        desc_marker = item.get_closest_marker("description")

        if desc_marker and desc_marker.args:
            description = desc_marker.args[0]

    report.tc_id = tc_id
    report.description = description
    report.test_name = (
        resolve_test_display_name(
            test_data,
            tc_id=str(tc_id) if tc_id else "",
            description=str(description) if description else "",
        )
        or description
    )

    if not report.test_name:
        report.test_name = description

    # ==========================
    # Log Result
    # ==========================
    status = report.outcome.upper()
    message = f"{status}: {report.test_name}"

    report.extras = getattr(report, "extras", [])

    report.extras.append(extras.text(message, name="Test Result"))

    test_case_ids_text = _get_test_case_ids_text(test_data)
    scenario_lines = _get_scenario_lines(test_data)
    if test_case_ids_text:
        report.extras.append(
            extras.text(
                test_case_ids_text,
                name="Test Case IDs",
            )
        )
        if scenario_lines:
            report.extras.append(
                extras.text(
                    "\n".join(scenario_lines),
                    name="Scenarios",
                )
            )
        if is_reportportal_enabled(item.config):
            attach_text_artifact("Test Case IDs", test_case_ids_text)
            if scenario_lines:
                attach_text_artifact("Scenarios", "\n".join(scenario_lines))

    # ==========================
    # Method Logs
    # ==========================
    method_logs = get_step_logs()

    if method_logs:
        report.extras.append(extras.text("\n".join(method_logs), name="Method Logs"))

        cast(Any, report).method_logs = method_logs

    if method_logs and is_reportportal_enabled(item.config):
        log_step_lines(method_logs)

    # ==========================
    # Console Logging
    # ==========================

    if report.passed:
        logger.success(message)

    elif report.skipped:
        logger.warning(message)

    else:
        logger.error(message)

    # ==========================
    # Screenshot Failed Only
    # ==========================

    if not report.failed:
        return

    page = cast(Any, item).funcargs.get("page")

    if page is None:
        report.extras.append(
            extras.text("No Playwright page fixture available", name="Failure Note")
        )

        return

    screenshot_dir = Path(settings.screenshot_dir)

    screenshot_dir.mkdir(parents=True, exist_ok=True)

    screenshot_name = report.test_name.replace(" ", "_").replace("/", "_").replace("|", "_")

    screenshot_path = screenshot_dir / f"{screenshot_name}.png"

    page.screenshot(path=screenshot_path, full_page=True)

    report.extras.append(extras.image(str(screenshot_path.absolute()), name="Failure Screenshot"))

    if is_reportportal_enabled(item.config):
        attach_failure_screenshot(page, report.test_name)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when not in {"setup", "call"}:
        return

    if report.when == "setup" and report.passed:
        return

    method_logs = getattr(report, "method_logs", [])

    for line in method_logs:
        safe_terminal_print(line)

    tc_id = getattr(report, "tc_id", "")
    test_name = report.nodeid.split("::")[-1]

    safe_terminal_print(f"[{report.outcome.upper()}] [{tc_id}] {test_name}")


def pytest_html_results_table_header(cells):
    cells[1] = "<th>Test Case</th>"


def pytest_html_results_table_row(report, cells):
    test_name = getattr(report, "test_name", report.nodeid)
    cells[1] = f"<td>{test_name}</td>"
