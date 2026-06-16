"""Root conftest — early hooks before tests/conftest.py is fully loaded."""

from __future__ import annotations

import os

from automation.reporting.reportportal_support import load_dotenv_for_reportportal


def pytest_load_initial_conftests(early_config: object, parser: object, args: list[str]) -> None:
    del early_config, parser
    load_dotenv_for_reportportal()
    if os.getenv("RP_API_KEY") and "--reportportal" not in args:
        args.append("--reportportal")
