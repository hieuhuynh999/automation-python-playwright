"""Load per-environment URLs and credentials from environments.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_ENVIRONMENTS_FILE = Path(__file__).with_name("environments.json")

PROFILE_FIELDS: frozenset[str] = frozenset(
    {
        "efms_base_url",
        "etms_base_url",
        "vfc_etms_base_url",
        "efms_account_username",
        "efms_account_password",
        "etms_account_username",
        "etms_account_password",
        "vfc_etms_account_username",
        "vfc_etms_account_password",
    }
)

PROFILE_FIELD_DEFAULTS: dict[str, str | None] = {
    "efms_base_url": "",
    "etms_base_url": "",
    "vfc_etms_base_url": "",
    "efms_account_username": None,
    "efms_account_password": None,
    "etms_account_username": None,
    "etms_account_password": None,
    "vfc_etms_account_username": None,
    "vfc_etms_account_password": None,
}


@lru_cache
def _load_environments() -> dict[str, dict[str, str]]:
    if not _ENVIRONMENTS_FILE.is_file():
        raise FileNotFoundError(
            f"Environment profiles file not found: {_ENVIRONMENTS_FILE}"
        )
    raw = json.loads(_ENVIRONMENTS_FILE.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid environments.json — expected object, got {type(raw)}")
    return {
        str(env_name).upper(): {
            str(key): str(value)
            for key, value in profile.items()
            if key in PROFILE_FIELDS and value is not None and str(value).strip()
        }
        for env_name, profile in raw.items()
        if isinstance(profile, dict)
    }


def available_environments() -> tuple[str, ...]:
    return tuple(sorted(_load_environments()))


def resolve_environment_profile(env: str) -> dict[str, str]:
    """Return URL/credential values for the given ENV name (UAT, DEV, …)."""
    key = str(env).strip().upper()
    profiles = _load_environments()
    if key not in profiles:
        known = ", ".join(sorted(profiles))
        raise ValueError(
            f"Unknown ENV '{env}'. Configure it in environments.json. Known: {known}"
        )
    return dict(profiles[key])


def _profile_field_overridden(settings: Any, field: str) -> bool:
    current = getattr(settings, field)
    default = PROFILE_FIELD_DEFAULTS[field]
    return current is not default


def apply_environment_profile(settings: Any) -> Any:
    """Merge environments.json profile; keep explicit .env / OS env overrides."""
    overrides = resolve_environment_profile(settings.env)
    for field, value in overrides.items():
        if _profile_field_overridden(settings, field):
            continue
        object.__setattr__(settings, field, value)

    missing = [
        field
        for field in sorted(PROFILE_FIELDS)
        if not getattr(settings, field, None)
    ]
    if missing:
        raise ValueError(
            f"ENV={settings.env} is missing required values in environments.json "
            f"(or set them in .env): {', '.join(missing)}"
        )
    return settings


def clear_environment_profile_cache() -> None:
    _load_environments.cache_clear()
