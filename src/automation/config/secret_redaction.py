from __future__ import annotations

import re

_QUOTED_ASSIGNMENT_PATTERNS = (
    re.compile(r"(efms_account_password\s*=\s*)(['\"]).*?\2"),
    re.compile(r"(etms_account_password\s*=\s*)(['\"]).*?\2"),
    re.compile(r"(account_password\s*=\s*)(['\"]).*?\2"),
    re.compile(r"(\bpassword\s*=\s*)(['\"]).*?\2", re.IGNORECASE),
)

# Chỉ khớp dòng .env (KEY=value), không đụng pytest locals (efms_account_password = '...')
_ENV_ASSIGNMENT_PATTERNS = (
    re.compile(r"(?:^|\n)(EFMS_ACCOUNT_PASSWORD=)(\S+)", re.IGNORECASE | re.MULTILINE),
    re.compile(r"(?:^|\n)(ETMS_ACCOUNT_PASSWORD=)(\S+)", re.IGNORECASE | re.MULTILINE),
)


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in _QUOTED_ASSIGNMENT_PATTERNS:
        redacted = pattern.sub(
            lambda match: f"{match.group(1)}{match.group(2)}***{match.group(2)}",
            redacted,
        )
    for pattern in _ENV_ASSIGNMENT_PATTERNS:
        redacted = pattern.sub(r"\1***", redacted)
    return redacted


def sanitize_test_report(report: object) -> None:
    """Redact secrets on pytest report before HTML / ReportPortal output."""
    longrepr = getattr(report, "longrepr", None)
    if longrepr is not None:
        text = str(longrepr)
        redacted = redact_secrets(text)
        if redacted != text:
            report.longrepr = redacted  # type: ignore[attr-defined]

    try:
        text = report.longreprtext  # type: ignore[attr-defined]
    except Exception:
        return

    redacted = redact_secrets(text)
    if redacted != text:
        report.longrepr = redacted  # type: ignore[attr-defined]
