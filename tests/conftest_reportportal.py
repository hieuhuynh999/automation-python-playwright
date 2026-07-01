"""ReportPortal hooks — loaded before main conftest via pytest_plugins."""

from __future__ import annotations

import os

import pytest

from automation.config import get_settings, reset_settings
from automation.logging import logger
from automation.reporting.reportportal_support import (
    apply_reportportal_display_names,
    apply_reportportal_patches,
    configure_reportportal_ini,
    load_dotenv_for_reportportal,
    should_enable_reportportal,
)
from automation.reporting.rerun_support import configure_pytest_reruns


def _invocation_args(config: pytest.Config) -> list[str]:
    return list(config.invocation_params.args)


def _apply_reportportal_session(
    config: pytest.Config,
    items: list[pytest.Item] | None = None,
) -> None:
    api_key = get_settings().rp_api_key or os.getenv("RP_API_KEY")
    no_reportportal = bool(getattr(config.option, "no_reportportal", False))
    args = _invocation_args(config)

    enable, reason = should_enable_reportportal(
        args,
        api_key=api_key,
        no_reportportal=no_reportportal,
    )
    if not enable:
        config.option.rp_enabled = False
        logger.info("ReportPortal SKIPPED: {}", reason)
        return

    rp_ready = configure_reportportal_ini(config, items)
    if not rp_ready:
        config.option.rp_enabled = False
        logger.warning(
            "ReportPortal SKIPPED: chạy riêng từng app — "
            "pytest -m efms hoặc pytest -m etms (hoặc tests/efms, tests/etms)",
        )
        return

    config.option.rp_enabled = True
    launch_name = config.getini("rp_launch")
    logger.info("ReportPortal ENABLED: {} ({})", launch_name, reason)
    if items is not None:
        apply_reportportal_display_names(items)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    load_dotenv_for_reportportal()
    reset_settings()
    configure_pytest_reruns(config)
    apply_reportportal_patches()
    _apply_reportportal_session(config)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    _apply_reportportal_session(config, items)
