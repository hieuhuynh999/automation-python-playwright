"""eTMS-specific pytest fixtures."""

from __future__ import annotations

import pytest

from automation.config import settings


@pytest.fixture()
def login_etms(pages, etms_account_password):
    """Login to eTMS, select branch, and wait for dashboard."""

    def _login(branch: str) -> None:
        pages.etms_login_page.open().login(
            settings.etms_username,
            etms_account_password,
        )
        assert pages.etms_login_page.is_branch_hub_selection_displayed()
        pages.etms_login_page.select_branch(branch)
        pages.etms_login_page.click_select_branch()
        assert pages.etms_home_page.is_home_url("app/default/home")
        assert pages.etms_home_page.is_dashboard_displayed()

    return _login
