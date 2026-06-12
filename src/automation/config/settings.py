from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "UAT"
    browser: str = "chrome"
    browser_headless: bool = False
    # Playwright default timeout
    browser_timeout: int = 30000
    # Page loading
    page_load_timeout: int = 60000
    # API timeout
    api_timeout: int = 30000
    # Database timeout
    db_timeout: int = 10000
    browser_slow_mo: int = 0
    polling_interval: int = 250

    efms_base_url: str = "https://uat-efms.logtechub.com/en/#/home"
    etms_base_url: str = "https://staging-itllog-etms.logtechub.com/en/#/app/default/home"
    api_base_url: str = "https://uat-efms.logtechub.com"
    account_username: str | None = Field(
        default=None,
        repr=False
    )
    account_password: str | None = Field(
        default=None,
        repr=False
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    db_url: str | None = None
    db_username: str | None = None
    db_password: str | None = Field(default=None, repr=False)

    screenshot_dir: str = "test-results/screenshots"
    trace_dir: str = "test-results/traces"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def playwright_channel(self) -> str:
        browser_name = self.browser.strip().lower()
        if browser_name == "edge":
            return "msedge"
        if browser_name == "chrome":
            return "chrome"
        raise ValueError(f"Unsupported browser: {self.browser}. Use chrome or edge.")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
