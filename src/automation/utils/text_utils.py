from __future__ import annotations


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def text_contains_any(text: str, hints: tuple[str, ...]) -> bool:
    normalized = normalize_text(text).casefold()
    return any(hint.casefold() in normalized for hint in hints)
