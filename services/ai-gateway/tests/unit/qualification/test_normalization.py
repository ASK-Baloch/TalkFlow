from app.realtime.qualification.normalization import (
    normalize_name,
    normalize_text,
)


def test_normalize_text():
    assert normalize_text("  YES, I Do! ") == "yes i do"


def test_normalize_name():
    assert normalize_name("john smith") == "John Smith"


def test_normalize_hyphenated_name():
    assert normalize_name("mary-jane smith") == "Mary-Jane Smith"


def test_normalize_apostrophe_name():
    assert normalize_name("john o'connor") == "John O'Connor"
