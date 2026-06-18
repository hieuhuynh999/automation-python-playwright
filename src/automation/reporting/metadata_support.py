from __future__ import annotations

from collections.abc import Iterable

from automation.config import settings


def _apps_from_paths(paths: Iterable[str]) -> set[str]:
    apps: set[str] = set()
    for raw in paths:
        path = raw.replace("\\", "/").lower()
        if "tests/efms" in path:
            apps.add("efms")
        if "tests/etms" in path:
            apps.add("etms")
    return apps


def _url_for_apps(apps: set[str]) -> str:
    if apps == {"efms"}:
        return settings.efms_base_url
    if apps == {"etms"}:
        return settings.etms_base_url
    return f"eFMS: {settings.efms_base_url} | eTMS: {settings.etms_base_url}"


def resolve_report_base_url(
    *,
    markexpr: str = "",
    test_paths: tuple[str, ...] = (),
    collected_item_paths: tuple[str, ...] = (),
) -> str:
    """Pick HTML report Base URL from collected tests, paths, or -m marker."""
    if collected_item_paths:
        return _url_for_apps(_apps_from_paths(collected_item_paths))

    apps = _apps_from_paths(test_paths)
    if len(apps) == 1:
        return _url_for_apps(apps)

    mark = markexpr.lower()
    if "etms" in mark and "efms" not in mark:
        return settings.etms_base_url
    if "efms" in mark and "etms" not in mark:
        return settings.efms_base_url

    return _url_for_apps(apps)
