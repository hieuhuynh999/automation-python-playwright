import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.smoke
@pytest.mark.login
@pytest.mark.efms
class TestEfmsAuth:
    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_auth_001_login_success_efms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_001")
    def test_smk_auth_001_login_success_efms(self, pages, data, efms_account_password):
        # Step 1: Open Login Page
        pages.efms_login_page.open()

        # Step 2: Enter Username (LOGIN_ADMIN)
        pages.efms_login_page.enter_username(settings.efms_username)

        # Step 3: Enter Password (LOGIN_ADMIN)
        pages.efms_login_page.enter_password(efms_account_password)

        # Step 4: Enter Company
        pages.efms_login_page.select_company(data["company"])

        # Step 5: Click Login
        pages.efms_login_page.click_login()

        # Expected: Dashboard displayed successfully
        assert pages.efms_home_page.is_dashboard_displayed()

    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_auth_002_logout_success_efms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_002")
    def test_smk_auth_002_logout_success_efms(self, pages, data, login_efms):
        # Precondition: Login success
        login_efms(data["company"])

        # Step 1: Click User Menu
        pages.efms_home_page.click_user_menu()

        # Step 2: Click Logout
        pages.efms_home_page.click_logout()

        # Step 3: Click "Yes" button
        pages.efms_home_page.click_confirm_yes()

        # Expected Result: Login page displayed
        assert pages.efms_login_page.is_login_page_displayed()
