"""ReportPortal hooks — loaded before main conftest via pytest_plugins."""

from __future__ import annotations

import os

import pytest

from automation.config import get_settings
from automation.logging import logger
from automation.reporting.reportportal_support import (
    apply_reportportal_display_names,
    configure_reportportal_ini,
    load_dotenv_for_reportportal,
)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    load_dotenv_for_reportportal()
    get_settings.cache_clear()
    rp_ready = configure_reportportal_ini(config)

    api_key = config.getini("rp_api_key") or os.getenv("RP_API_KEY")
    if api_key and rp_ready:
        config.option.rp_enabled = True
    elif api_key:
        config.option.rp_enabled = False
    elif getattr(config.option, "rp_enabled", False):
        config.option.rp_enabled = False
        logger.warning(
            "ReportPortal disabled: set RP_API_KEY in .env (ReportPortal UI → Profile → API Keys)"
        )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    api_key = config.getini("rp_api_key") or os.getenv("RP_API_KEY")
    if not api_key:
        return

    rp_ready = configure_reportportal_ini(config, items)
    if rp_ready:
        config.option.rp_enabled = True
        apply_reportportal_display_names(items)
        launch_name = config.getini("rp_launch")
        logger.info("ReportPortal launch: {}", launch_name)
        return

    config.option.rp_enabled = False
    logger.warning(
        "ReportPortal disabled: chạy riêng từng app — "
        "pytest -m efms hoặc pytest -m etms (hoặc tests/efms, tests/etms)"
    )
