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


@pytest.fixture()
def login_vfc_etms(pages, vfc_etms_account_password):
    """Login to VFC eTMS, select branch, and wait for dashboard."""

    def _login(branch: str) -> None:
        username = settings.vfc_etms_username
        if not username:
            pytest.skip("Set VFC_ETMS_ACCOUNT_USERNAME to run VFC eTMS login tests")

        vfc_login = pages.etms_vfc_login_page
        vfc_login.open().login(username, vfc_etms_account_password)
        vfc_login.select_branch(branch)
        vfc_login.click_select_branch()
        assert pages.etms_home_page.is_home_url("app/default/home")
        assert pages.etms_home_page.is_dashboard_displayed()

    return _login
