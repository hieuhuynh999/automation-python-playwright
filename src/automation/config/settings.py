"""Runtime configuration — .env + environments.json (via ENV)."""

from __future__ import annotations

from functools import lru_cache
from typing import Final, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from automation.config.environment_profiles import apply_environment_profile

_ENV_FILE: Final = ".env"


class Settings(BaseSettings):
    """Framework settings.

    Runtime (browser, timeouts, ReportPortal) → ``.env`` / OS environment.
    Application URLs & credentials → ``environments.json`` keyed by ``ENV`` (UAT, DEV, …).
    Individual fields may be overridden in ``.env`` (e.g. ``VFC_ETMS_BASE_URL``).
    """

    # --- Runtime ---
    env: str = "UAT"

    # --- Browser ---
    browser: str = "chrome"
    browser_headless: bool = False
    browser_timeout: int = 60_000
    browser_slow_mo: int = 0
    page_load_timeout: int = 60_000
    component_interaction_timeout: int = 15_000
    quick_action_timeout: int = 5_000
    tab_switch_timeout: int = 10_000
    polling_interval: int = 250
    open_url_settle_ms: int = 5_000
    navigation_settle_ms: int = 1_000
    headless_viewport_width: int = 1920
    headless_viewport_height: int = 1080

    # --- Application profile (defaults empty — filled from environments.json) ---
    efms_base_url: str = ""
    etms_base_url: str = ""
    vfc_etms_base_url: str = ""
    efms_account_username: str | None = Field(default=None, repr=False)
    efms_account_password: str | None = Field(default=None, repr=False)
    etms_account_username: str | None = Field(default=None, repr=False)
    etms_account_password: str | None = Field(default=None, repr=False)
    vfc_etms_account_username: str | None = Field(default=None, repr=False)
    vfc_etms_account_password: str | None = Field(default=None, repr=False)
    account_username: str | None = Field(default=None, repr=False)
    account_password: str | None = Field(default=None, repr=False)

    # --- Artifacts ---
    screenshot_dir: str = "test-results/screenshots"

    # --- ReportPortal ---
    rp_endpoint: str = "http://localhost:8080"
    rp_project: str = "default_personal"
    rp_api_key: str | None = Field(default=None, repr=False)
    rp_verify_ssl: bool = False

    # --- Pytest retry ---
    test_reruns: int = 1
    test_reruns_delay: int = 2

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _merge_environment_profile(self) -> Self:
        return apply_environment_profile(self)

    # --- Credential aliases (eFMS legacy fallbacks) ---

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

    # --- Derived timeouts ---

    @property
    def network_idle_timeout(self) -> int:
        return min(self.component_interaction_timeout, self.page_load_timeout)

    @property
    def bounded_probe_timeout(self) -> int:
        return min(self.component_interaction_timeout, self.browser_timeout)


class SettingsFactory:
    """Build and cache :class:`Settings` instances."""

    @staticmethod
    def create() -> Settings:
        return Settings()

    @staticmethod
    @lru_cache
    def get_cached() -> Settings:
        return SettingsFactory.create()

    @staticmethod
    def reset() -> None:
        from automation.config.environment_profiles import clear_environment_profile_cache

        SettingsFactory.get_cached.cache_clear()
        clear_environment_profile_cache()


def get_settings() -> Settings:
    return SettingsFactory.get_cached()


def reset_settings() -> None:
    """Clear cached settings (e.g. after changing ENV in tests)."""
    SettingsFactory.reset()


class _SettingsProxy:
    """Module-level accessor — always reads through the settings cache."""

    def __getattr__(self, name: str) -> object:
        return getattr(get_settings(), name)


settings = _SettingsProxy()
