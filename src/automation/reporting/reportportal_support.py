from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from reportportal_client import RPLogger

if TYPE_CHECKING:
    from playwright.sync_api import Page

_RP_LOGGER: logging.Logger | None = None


def _load_dotenv_early() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def load_dotenv_for_reportportal() -> None:
    _load_dotenv_early()


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


def resolve_launch_for_run(marker_expr: str | None, settings: Any) -> tuple[str, str, str]:
    """Return ReportPortal launch name, description, and attributes for this run."""
    base_attrs = f"'Environment:{settings.env}' 'Framework:pytest-playwright'"
    application = detect_application_from_marker(marker_expr)

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

    launch = settings.rp_launch
    description = settings.rp_launch_description
    attributes = settings.rp_launch_attributes or base_attrs
    if "Application:" not in attributes:
        attributes = f"{attributes} 'Application:efms-etms'"
    return launch, description, attributes


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


def configure_reportportal_ini(config: pytest.Config) -> None:
    from automation.config import get_settings

    settings = get_settings()
    api_key = settings.rp_api_key or os.getenv("RP_API_KEY")
    if not api_key:
        return

    marker_expr = getattr(config.option, "markexpr", "") or ""
    launch_name, launch_description, launch_attributes = resolve_launch_for_run(
        marker_expr,
        settings,
    )

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
