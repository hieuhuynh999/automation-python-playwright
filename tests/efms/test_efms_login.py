import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.parametrize("data", DataProvider.efms_cases("test_login_efms"))
@pytest.mark.login
@pytest.mark.smoke
@pytest.mark.efms
def test_login_efms(pages, data, account_password):
    pages.efms_login_page.open().login(
        settings.account_username,
        account_password,
        data["company"],
    )

    assert pages.efms_home_page.verify_logo_title(data["title"])
