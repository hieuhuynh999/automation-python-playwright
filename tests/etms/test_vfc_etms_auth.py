import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.smoke
@pytest.mark.login
@pytest.mark.etms
@pytest.mark.vfc_etms
class TestVfcEtmsAuth:
    @pytest.mark.parametrize(
        "data",
        DataProvider.vfc_etms_cases("test_vfc_smk_auth_001_login_select_branch_etms"),
    )
    @pytest.mark.tc_id("VFC_SMK_AUTH_001")
    def test_vfc_smk_auth_001_login_select_branch_etms(
        self,
        pages,
        data,
        vfc_etms_account_password,
    ):
        username = settings.vfc_etms_username
        if not username:
            pytest.skip("Set VFC_ETMS_ACCOUNT_USERNAME to run VFC eTMS login tests")

        vfc_login = pages.etms_vfc_login_page

        # Step 1: Open VFC eTMS login page
        vfc_login.open()

        # Step 2–4: Login
        vfc_login.login(username, vfc_etms_account_password)
        assert vfc_login.is_branch_hub_selection_displayed()

        # Step 5: Select Branch/Hub VNHCM (search txtSearchAll → select option)
        vfc_login.select_branch(data["branch"])

        # Step 6: Click Select
        vfc_login.click_select_branch(data["expected_url_contains"])

        # Expected: Home page — URL + title "eTMS"
        assert pages.etms_home_page.is_home_url(data["expected_url_contains"])
        assert pages.etms_home_page.is_dashboard_displayed()
        assert pages.etms_home_page.is_etms_title_displayed(data["expected_page_title"])
