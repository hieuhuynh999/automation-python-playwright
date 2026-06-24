"""Unit tests for retry helpers and secret redaction in reports."""

import os

from automation.config.secret_redaction import redact_secrets, sanitize_test_report
from automation.reporting.metadata_support import resolve_report_base_url
from automation.reporting.reportportal_support import (
    _load_dotenv_early,
    _project_env_path,
    is_pytest_execution_run,
    resolve_launch_for_run,
    should_auto_enable_reportportal,
    should_enable_reportportal,
)
from automation.reporting.rerun_support import is_rerun_report


class _FakeReport:
    def __init__(self, outcome: str) -> None:
        self.outcome = outcome


def test_is_rerun_report_true() -> None:
    assert is_rerun_report(_FakeReport("rerun")) is True


def test_is_rerun_report_false() -> None:
    assert is_rerun_report(_FakeReport("failed")) is False
    assert is_rerun_report(None) is False


def test_redact_secrets_fixture_assignment() -> None:
    text = "data = {'preconditions': 'Login success'}\nefms_account_password = 'any-new-pass'"
    redacted = redact_secrets(text)
    assert "efms_account_password = '***'" in redacted
    assert "any-new-pass" not in redacted


def test_redact_secrets_password_local() -> None:
    text = "password = 'secret-from-env'"
    assert redact_secrets(text) == "password = '***'"


def test_redact_secrets_env_var_line() -> None:
    text = "EFMS_ACCOUNT_PASSWORD=secret-from-env"
    assert redact_secrets(text) == "EFMS_ACCOUNT_PASSWORD=***"


def test_sanitize_test_report_redacts_longreprtext() -> None:
    class _Report:
        longrepr = (
            "data = {'company': 'LTH Demo JSC'}\n"
            "efms_account_password = 'dummy-value-for-redaction-test'"
        )

        @property
        def longreprtext(self) -> str:
            return str(self.longrepr)

    report = _Report()
    sanitize_test_report(report)
    assert "dummy-value-for-redaction-test" not in report.longreprtext
    assert "efms_account_password = '***'" in report.longreprtext


def test_resolve_report_base_url_efms_marker() -> None:
    url = resolve_report_base_url(markexpr="efms")
    assert "uat-efms" in url
    assert "etms" not in url.lower() or "efms" in url.lower()


def test_resolve_report_base_url_etms_path() -> None:
    url = resolve_report_base_url(
        collected_item_paths=("tests/etms/test_etms_auth.py",),
    )
    assert "etms" in url.lower()


def test_resolve_report_base_url_mixed_suite() -> None:
    url = resolve_report_base_url(
        collected_item_paths=(
            "tests/efms/test_efms_auth.py",
            "tests/etms/test_etms_auth.py",
        ),
    )
    assert "eFMS:" in url
    assert "eTMS:" in url


def test_is_pytest_execution_run_collect_only() -> None:
    assert is_pytest_execution_run(["--collect-only", "tests"]) is False
    assert is_pytest_execution_run(["-v", "tests/etms"]) is True


def test_should_auto_enable_reportportal_skips_collect_only() -> None:
    assert should_auto_enable_reportportal(["--collect-only", "tests"]) is False


def test_should_enable_reportportal_no_flag() -> None:
    enabled, reason = should_enable_reportportal(
        ["tests/etms"],
        api_key="key",
        no_reportportal=True,
    )
    assert enabled is False
    assert "no-reportportal" in reason


def test_should_enable_reportportal_execution() -> None:
    enabled, reason = should_enable_reportportal(
        ["tests/etms", "-m", "etms"],
        api_key="key",
    )
    assert enabled is True
    assert "RP_API_KEY" in reason


def test_project_env_path_points_to_repo_root() -> None:
    assert _project_env_path().name == ".env"
    assert _project_env_path().parent.name == "automation-techub"


def test_load_dotenv_early_overrides_stale_rp_launch_etms(monkeypatch) -> None:
    monkeypatch.delenv("RP_LAUNCH_ETMS", raising=False)
    monkeypatch.setenv("RP_LAUNCH_ETMS", "etms-automation")

    _load_dotenv_early()

    launch = resolve_launch_for_run(
        marker_expr="",
        args=["tests/etms/test_etms_performance.py"],
        items=None,
        settings=type("S", (), {"env": "UAT"})(),
    )
    assert launch is not None
    assert launch[0] != "etms-automation"
    assert os.getenv("RP_LAUNCH_ETMS") != "etms-automation"
