from app.realtime.qualification.validators import (
    validate_age,
    validate_name,
    validate_zip_code,
)


def test_valid_name():
    assert validate_name("Daniel Smith")


def test_valid_single_name():
    assert validate_name("Daniel")


def test_valid_age():
    assert validate_age(67)


def test_invalid_age():
    assert not validate_age(250)


def test_valid_zip():
    assert validate_zip_code("75001")


def test_invalid_zip():
    assert not validate_zip_code("7500")
