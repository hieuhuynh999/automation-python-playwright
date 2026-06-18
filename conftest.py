"""Root conftest — early hooks before tests/conftest.py is fully loaded."""

from __future__ import annotations

import pytest

from automation.reporting.reportportal_support import (
    load_dotenv_for_reportportal,
    should_auto_enable_reportportal,
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--no-reportportal",
        action="store_true",
        default=False,
        help="Do not send results to ReportPortal (overrides RP_API_KEY auto-enable)",
    )


def pytest_load_initial_conftests(early_config: object, parser: object, args: list[str]) -> None:
    del early_config, parser
    load_dotenv_for_reportportal()
    if should_auto_enable_reportportal(args):
        args.append("--reportportal")
