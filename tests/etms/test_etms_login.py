import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.parametrize("data", DataProvider.etms_cases("test_login_etms"))
@pytest.mark.login
@pytest.mark.smoke
@pytest.mark.etms
def test_login_etms(pages, data, etms_account_password):
    pages.etms_home_page.open().login(
        settings.etms_username,
        etms_account_password,
    )

    assert not pages.etms_home_page.is_password_field_visible()
    assert data["expected_url_contains"] in pages.etms_home_page.current_url
