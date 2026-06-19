import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.smoke
@pytest.mark.login
@pytest.mark.etms
class TestEtmsAuth:
    @pytest.mark.parametrize(
        "data", DataProvider.etms_cases("test_smk_auth_001_login_success_etms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_001")
    def test_smk_auth_001_login_success_etms(self, pages, data, etms_account_password):
        # Step 1: Open Login Page
        pages.etms_login_page.open()

        # Step 2: Enter Username
        pages.etms_login_page.enter_username(settings.etms_username)

        # Step 3: Enter Password
        pages.etms_login_page.enter_password(etms_account_password)

        # Step 4: Click Login
        pages.etms_login_page.click_login()

        # Expected: Login đúng — hiển thị màn hình chọn Branch/Hub
        assert pages.etms_login_page.is_branch_hub_selection_displayed()

    @pytest.mark.parametrize(
        "data", DataProvider.etms_cases("test_smk_auth_002_select_branch_etms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_002")
    def test_smk_auth_002_select_branch_etms(self, pages, data, etms_account_password):
        # Precondition: Login success
        pages.etms_login_page.open().login(
            settings.etms_username,
            etms_account_password,
        )
        assert pages.etms_login_page.is_branch_hub_selection_displayed()

        # Step 1–2: Select Branch/Hub — Choose Branch VNHCM
        pages.etms_login_page.select_branch(data["branch"])
        assert pages.etms_login_page.is_branch_selected(data["branch"])

        # Step 3: Click Select
        pages.etms_login_page.click_select_branch()

        # Expected: Chọn branch thành công — vào trang Home
        assert pages.etms_home_page.is_home_url(data["expected_url_contains"])
        assert pages.etms_home_page.is_dashboard_displayed()
