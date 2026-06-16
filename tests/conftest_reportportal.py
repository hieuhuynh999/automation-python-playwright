"""ReportPortal hooks — loaded before main conftest via pytest_plugins."""

from __future__ import annotations

import os

import pytest

from automation.config import get_settings
from automation.logging import logger
from automation.reporting.reportportal_support import (
    apply_reportportal_display_names,
    configure_reportportal_ini,
    is_reportportal_enabled,
    load_dotenv_for_reportportal,
)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    load_dotenv_for_reportportal()
    get_settings.cache_clear()
    configure_reportportal_ini(config)

    api_key = config.getini("rp_api_key") or os.getenv("RP_API_KEY")
    if api_key:
        config.option.rp_enabled = True
    elif getattr(config.option, "rp_enabled", False):
        config.option.rp_enabled = False
        logger.warning(
            "ReportPortal disabled: set RP_API_KEY in .env "
            "(ReportPortal UI → Profile → API Keys)"
        )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if is_reportportal_enabled(config):
        apply_reportportal_display_names(items)
