"""Unit tests for retry helpers and secret redaction in reports."""

from automation.config.secret_redaction import redact_secrets, sanitize_test_report
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
            "efms_account_password = '12345678'"
        )

        @property
        def longreprtext(self) -> str:
            return str(self.longrepr)

    report = _Report()
    sanitize_test_report(report)
    assert "12345678" not in report.longreprtext
    assert "efms_account_password = '***'" in report.longreprtext
