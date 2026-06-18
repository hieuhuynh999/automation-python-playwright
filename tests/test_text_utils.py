from automation.utils.text_utils import normalize_text, text_contains_any


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("  Hồ   Chí   Minh  ") == "Hồ Chí Minh"


def test_text_contains_any_matches_hint() -> None:
    assert text_contains_any("Branch: Hồ Chí Minh (VNHCM)", ("VNHCM", "Hồ Chí Minh"))


def test_text_contains_any_no_match() -> None:
    assert not text_contains_any("VNHAN", ("VNHCM", "Hồ Chí Minh"))
