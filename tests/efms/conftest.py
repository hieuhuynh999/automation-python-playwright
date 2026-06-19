"""eFMS-specific pytest fixtures."""

from __future__ import annotations

import pytest

from automation.config import settings


@pytest.fixture()
def login_efms(pages, efms_account_password):
    """Login to eFMS and wait for dashboard — reuse across eFMS tests."""

    def _login(company: str) -> None:
        pages.efms_login_page.open().login(
            settings.efms_username,
            efms_account_password,
            company,
        )
        assert pages.efms_home_page.is_dashboard_displayed()
        pages.efms_home_page.wait_for_dashboard_ready()

    return _login
