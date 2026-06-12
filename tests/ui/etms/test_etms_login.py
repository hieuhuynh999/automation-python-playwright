import pytest

from automation.config import settings

@pytest.mark.tc_id("ETMS-LOGIN-001")
@pytest.mark.description("Login eTMS Successfully")
@pytest.mark.login
@pytest.mark.etmss
def test_login_etms(pages):
    pages.etms_home_page.open().login(settings.account_username, settings.account_password)
    assert not pages.etms_home_page.is_password_field_visible()
    assert "staging-itllog-etms.logtechub.com" in pages.etms_home_page.current_url
