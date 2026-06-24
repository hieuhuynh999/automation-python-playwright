from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "UAT"
    browser: str = "chrome"
    browser_headless: bool = False
    browser_timeout: int = 60000
    page_load_timeout: int = 60000
    browser_slow_mo: int = 0
    polling_interval: int = 250
    open_url_settle_ms: int = 5000
    navigation_settle_ms: int = 1000
    headless_viewport_width: int = 1920
    headless_viewport_height: int = 1080
    efms_base_url: str = "https://uat-efms.logtechub.com/"
    etms_base_url: str = "https://staging-itllog-etms.logtechub.com/en/#/app/default/home"
    vfc_etms_base_url: str = "https://test-vfc-etms.logtechub.com/en/#/"
    efms_account_username: str | None = Field(default=None, repr=False)
    efms_account_password: str | None = Field(default=None, repr=False)
    etms_account_username: str | None = Field(default=None, repr=False)
    etms_account_password: str | None = Field(default=None, repr=False)
    vfc_etms_account_username: str | None = Field(default=None, repr=False)
    vfc_etms_account_password: str | None = Field(default=None, repr=False)
    account_username: str | None = Field(default=None, repr=False)
    account_password: str | None = Field(default=None, repr=False)

    screenshot_dir: str = "test-results/screenshots"

    rp_endpoint: str = "http://localhost:8080"
    rp_project: str = "default_personal"
    rp_api_key: str | None = Field(default=None, repr=False)
    rp_verify_ssl: bool = False

    test_reruns: int = 1
    test_reruns_delay: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def efms_username(self) -> str | None:
        return self.efms_account_username or self.account_username

    @property
    def efms_password(self) -> str | None:
        return self.efms_account_password or self.account_password

    @property
    def etms_username(self) -> str | None:
        return self.etms_account_username

    @property
    def etms_password(self) -> str | None:
        return self.etms_account_password

    @property
    def vfc_etms_username(self) -> str | None:
        return self.vfc_etms_account_username

    @property
    def vfc_etms_password(self) -> str | None:
        return self.vfc_etms_account_password


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
