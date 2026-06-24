from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from reportportal_client import RPLogger

from automation.config.secret_redaction import redact_secrets, sanitize_test_report
from automation.reporting.rerun_support import is_rerun_report

if TYPE_CHECKING:
    from playwright.sync_api import Page

_RP_LOGGER: logging.Logger | None = None
_RP_PATCH_APPLIED = False

_NON_EXECUTION_FLAGS = frozenset(
    {
        "--collect-only",
        "--co",
        "--fixtures",
        "--funcargs",
        "--markers",
        "--version",
        "--help",
        "--setup-only",
        "--setup-show",
    }
)


def is_pytest_execution_run(args: list[str]) -> bool:
    """False for IDE discovery and other non-execute pytest invocations."""
    for arg in args:
        if arg in _NON_EXECUTION_FLAGS or arg == "-h":
            return False
    return True


def non_execution_reason(args: list[str]) -> str:
    for arg in args:
        if arg == "--collect-only" or arg == "--co":
            return "pytest --collect-only (IDE test discovery)"
        if arg in _NON_EXECUTION_FLAGS or arg == "-h":
            return f"pytest {arg} (not a test execution)"
    return "not a test execution"


def should_auto_enable_reportportal(args: list[str]) -> bool:
    """Whether root conftest should inject --reportportal into CLI args."""
    if "--no-reportportal" in args:
        return False
    if "--reportportal" in args:
        return True
    if not os.getenv("RP_API_KEY"):
        return False
    return is_pytest_execution_run(args)


def should_enable_reportportal(
    args: list[str],
    *,
    api_key: str | None,
    no_reportportal: bool = False,
) -> tuple[bool, str]:
    """Decide if ReportPortal should run; second value is log reason."""
    if no_reportportal:
        return False, "disabled via --no-reportportal"
    if not is_pytest_execution_run(args):
        return False, non_execution_reason(args)
    if not api_key:
        if "--reportportal" in args:
            return False, "RP_API_KEY not set (--reportportal ignored)"
        return False, "RP_API_KEY not set"
    return True, "test execution with RP_API_KEY"


def load_dotenv_for_reportportal() -> None:
    _load_dotenv_early()


def _project_env_path() -> Path:
    # reportportal_support.py → reporting → automation → src → repo root
    return Path(__file__).resolve().parents[3] / ".env"


def _load_dotenv_early() -> None:
    env_path = _project_env_path()
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        # Project .env is the local source of truth (overrides stale shell vars).
        os.environ[key.strip()] = value.strip()


def detect_application_from_marker(marker_expr: str | None) -> str | None:
    if not marker_expr:
        return None

    expr = marker_expr.lower()
    has_efms = "efms" in expr
    has_etms = "etms" in expr
    if has_efms and not has_etms:
        return "efms"
    if has_etms and not has_efms:
        return "etms"
    return None


def detect_application_from_paths(args: list[str]) -> str | None:
    has_efms = False
    has_etms = False

    for arg in args:
        if arg.startswith("-"):
            continue
        normalized = arg.replace("\\", "/").lower()
        if "tests/efms" in normalized or normalized.endswith("/efms"):
            has_efms = True
        if "tests/etms" in normalized or normalized.endswith("/etms"):
            has_etms = True

    if has_efms and not has_etms:
        return "efms"
    if has_etms and not has_efms:
        return "etms"
    return None


def detect_application_from_items(items: list[pytest.Item]) -> str | None:
    apps: set[str] = set()

    for item in items:
        if item.get_closest_marker("efms"):
            apps.add("efms")
        if item.get_closest_marker("etms"):
            apps.add("etms")

    if apps == {"efms"}:
        return "efms"
    if apps == {"etms"}:
        return "etms"
    return None


def detect_application_for_run(
    *,
    marker_expr: str | None = None,
    args: list[str] | None = None,
    items: list[pytest.Item] | None = None,
) -> str | None:
    for detector in (
        lambda: detect_application_from_marker(marker_expr),
        lambda: detect_application_from_paths(args or []),
        lambda: detect_application_from_items(items or []),
    ):
        application = detector()
        if application:
            return application
    return None


def resolve_launch_for_run(
    *,
    marker_expr: str | None = None,
    args: list[str] | None = None,
    items: list[pytest.Item] | None = None,
    settings: Any,
) -> tuple[str, str, str] | None:
    """Return ReportPortal launch name, description, and attributes for this run."""
    base_attrs = f"'Environment:{settings.env}' 'Framework:pytest-playwright'"
    application = detect_application_for_run(
        marker_expr=marker_expr,
        args=args,
        items=items,
    )

    if application == "efms":
        launch = os.getenv("RP_LAUNCH_EFMS", "efms-automation")
        description = os.getenv("RP_LAUNCH_DESCRIPTION_EFMS", "eFMS UI automation")
        attributes = f"{base_attrs} 'Application:efms'"
        return launch, description, attributes

    if application == "etms":
        launch = os.getenv("RP_LAUNCH_ETMS", "etms-automation")
        description = os.getenv("RP_LAUNCH_DESCRIPTION_ETMS", "eTMS UI automation")
        attributes = f"{base_attrs} 'Application:etms'"
        return launch, description, attributes

    return None


def resolve_test_display_name(
    test_data: Any,
    *,
    tc_id: str = "",
    description: str = "",
) -> str:
    if isinstance(test_data, dict):
        test_case_ids = test_data.get("test_case_ids")
        if isinstance(test_case_ids, list):
            tc_id = tc_id or " | ".join(str(value) for value in test_case_ids if value)
        elif test_case_ids:
            tc_id = tc_id or str(test_case_ids)
        else:
            test_case_id = test_data.get("test_case_id")
            if test_case_id:
                tc_id = tc_id or str(test_case_id)

        row_description = test_data.get("description")
        if row_description:
            description = description or str(row_description)

    if tc_id and description:
        return f"{tc_id} - {description}"
    if tc_id:
        return tc_id
    return description


def build_reportportal_display_name(item: pytest.Item) -> str | None:
    test_data = None
    if hasattr(item, "callspec") and item.callspec is not None:
        test_data = item.callspec.params.get("data")

    tc_id = ""
    description = ""

    tc_id_marker = item.get_closest_marker("tc_id")
    if tc_id_marker and tc_id_marker.args:
        tc_id = str(tc_id_marker.args[0])

    desc_marker = item.get_closest_marker("description")
    if desc_marker and desc_marker.args:
        description = str(desc_marker.args[0])

    display_name = resolve_test_display_name(
        test_data,
        tc_id=tc_id,
        description=description,
    )
    return display_name or None


def apply_reportportal_display_names(items: list[pytest.Item]) -> None:
    for item in items:
        display_name = build_reportportal_display_name(item)
        if display_name:
            item.add_marker(pytest.mark.name(display_name))


def is_reportportal_enabled(config: pytest.Config) -> bool:
    if getattr(config, "_rp_enabled", False):
        return True

    if not config.pluginmanager.hasplugin("reportportal"):
        return False

    option = getattr(config.option, "rp_enabled", None)
    if option is not None:
        return bool(option)

    return "--reportportal" in config.invocation_params.args


def configure_reportportal_ini(
    config: pytest.Config,
    items: list[pytest.Item] | None = None,
) -> bool:
    """Inject ReportPortal ini values. Returns True when RP should run for this session."""
    from automation.config import get_settings

    settings = get_settings()
    api_key = settings.rp_api_key or os.getenv("RP_API_KEY")
    if not api_key:
        return False

    marker_expr = getattr(config.option, "markexpr", "") or ""
    launch = resolve_launch_for_run(
        marker_expr=marker_expr,
        args=list(config.args),
        items=items,
        settings=settings,
    )

    if launch is None:
        for key in ("rp_launch", "rp_launch_description", "rp_launch_attributes"):
            config._inicache.pop(key, None)  # noqa: SLF001
        return False

    launch_name, launch_description, launch_attributes = launch
    ini_map = {
        "rp_endpoint": settings.rp_endpoint,
        "rp_project": settings.rp_project,
        "rp_api_key": api_key,
        "rp_launch": launch_name,
        "rp_launch_description": launch_description,
        "rp_verify_ssl": str(settings.rp_verify_ssl).lower(),
        "rp_launch_attributes": launch_attributes,
    }

    for key, value in ini_map.items():
        if value:
            config._inicache[key] = value  # noqa: SLF001 — pytest-reportportal pattern

    return True


def get_rp_logger() -> logging.Logger | None:
    global _RP_LOGGER
    if _RP_LOGGER is not None:
        return _RP_LOGGER

    logging.setLoggerClass(RPLogger)
    logger = logging.getLogger("automation.reportportal")
    logger.setLevel(logging.INFO)
    _RP_LOGGER = logger
    return logger


def log_step_lines(lines: list[str]) -> None:
    rp_logger = get_rp_logger()
    if rp_logger is None or not lines:
        return

    rp_logger.info("Method logs:\n%s", "\n".join(lines))


def attach_failure_screenshot(page: Page, test_name: str) -> None:
    rp_logger = get_rp_logger()
    if rp_logger is None:
        return

    screenshot_bytes = page.screenshot(full_page=True)
    safe_name = test_name.replace(" ", "_").replace("/", "_").replace("|", "_").replace(":", "_")
    rp_logger.info(
        "Failure screenshot",
        attachment={
            "name": f"{safe_name}.png",
            "data": screenshot_bytes,
            "mime": "image/png",
        },
    )


def attach_text_artifact(name: str, content: str) -> None:
    rp_logger = get_rp_logger()
    if rp_logger is None or not content:
        return

    rp_logger.info(
        name,
        attachment={
            "name": f"{name}.txt",
            "data": content.encode("utf-8"),
            "mime": "text/plain",
        },
    )


def apply_reportportal_patches() -> None:
    """Patch ReportPortal agent: skip rerun attempts + redact passwords in failure logs."""
    global _RP_PATCH_APPLIED
    if _RP_PATCH_APPLIED:
        return

    try:
        from pytest_reportportal.service import PyTestService
    except ImportError:
        return

    original_process = PyTestService.process_results
    original_post_log = PyTestService.post_log

    def process_results_patched(
        self: Any,
        test_item: pytest.Item,
        report: pytest.TestReport,
    ) -> None:
        if is_rerun_report(report):
            return
        sanitize_test_report(report)
        original_process(self, test_item, report)

    def post_log_patched(
        self: Any,
        test_item: pytest.Item,
        message: str,
        log_level: str = "INFO",
        attachment: Any | None = None,
    ) -> None:
        original_post_log(
            self,
            test_item,
            redact_secrets(str(message)),
            log_level=log_level,
            attachment=attachment,
        )

    PyTestService.process_results = process_results_patched  # type: ignore[method-assign]
    PyTestService.post_log = post_log_patched  # type: ignore[method-assign]
    _RP_PATCH_APPLIED = True
