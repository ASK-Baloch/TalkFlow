import pytest
from app.call_id import (
    validate_call_id,
)


def test_valid_call_id():
    value = "96cfeefd-fc31-4ac7-b856-74f7ff717ab8"

    assert validate_call_id(value) == value


def test_path_traversal_rejected():
    with pytest.raises(ValueError):
        validate_call_id("../../etc/passwd")
