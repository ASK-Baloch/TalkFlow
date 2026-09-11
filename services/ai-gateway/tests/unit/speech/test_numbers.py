from app.realtime.speech.numbers import (
    digits_to_words,
    integer_to_words,
)


def test_digits_to_words():
    assert digits_to_words("75001") == ("seven five zero zero one")


def test_leading_zero_preserved():
    assert digits_to_words("07442") == ("zero seven four four two")


def test_integer_age():
    assert integer_to_words(67) == "sixty seven"


def test_integer_hundred():
    assert integer_to_words(100) == "one hundred"
