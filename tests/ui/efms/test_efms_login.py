import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.parametrize(
    "data",
    DataProvider.efms(
        "test_login_efms"
    )
)
@pytest.mark.login
@pytest.mark.efms
def test_login_efms(
    pages,
    data
):

    pages.efms_home_page.open().login(
        settings.account_username,
        settings.account_password,
        data["company"]
    )

    assert (
        pages.efms_home_page
        .verify_logo_title(data["title"])
    )
