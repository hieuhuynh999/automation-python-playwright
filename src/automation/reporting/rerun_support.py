from __future__ import annotations

import sys

import pytest

from automation.config import get_settings


def is_rerun_report(report: pytest.TestReport | None) -> bool:
    """True for intermediate failed attempts that pytest-rerunfailures will retry."""
    return bool(report and getattr(report, "outcome", None) == "rerun")


def configure_pytest_reruns(config: pytest.Config) -> None:
    """Apply rerun count/delay from settings (.env: TEST_RERUNS, TEST_RERUNS_DELAY).

    CLI flags ``--reruns`` / ``--reruns-delay`` take precedence when explicitly passed.
    """
    settings = get_settings()
    argv = sys.argv
    reruns_on_cli = any(arg == "--reruns" or arg.startswith("--reruns=") for arg in argv)
    delay_on_cli = any(
        arg == "--reruns-delay" or arg.startswith("--reruns-delay=") for arg in argv
    )

    if not reruns_on_cli:
        config.option.reruns = settings.test_reruns
    if not delay_on_cli:
        config.option.reruns_delay = settings.test_reruns_delay
