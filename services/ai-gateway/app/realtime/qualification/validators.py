from __future__ import annotations

import re


def validate_name(
    value: str | None,
) -> bool:
    if not value:
        return False

    parts = value.split()

    if not (1 <= len(parts) <= 5):
        return False

    for part in parts:
        cleaned = part.replace(
            "'",
            "",
        ).replace(
            "-",
            "",
        ).replace(
            ".",
            "",
        ).replace(
            ",",
            "",
        )

        if not cleaned.isalpha():
            return False

    return True


def validate_age(
    value: int | None,
) -> bool:
    if value is None:
        return False

    # This validates plausibility, not qualification.
    return 18 <= value <= 120


def validate_zip_code(
    value: str | None,
    *,
    expected_length: int = 5,
) -> bool:
    if value is None:
        return False

    return bool(
        re.fullmatch(
            rf"\d{{{expected_length}}}",
            value,
        )
    )


def validate_boolean(
    value: bool | None,
) -> bool:
    return value is not None
