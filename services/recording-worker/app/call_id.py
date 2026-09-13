from __future__ import annotations

from uuid import UUID


def validate_call_id(
    value: str,
) -> str:
    try:
        parsed = UUID(value)

    except ValueError as exc:
        raise ValueError("Invalid TalkFlow call UUID") from exc

    canonical = str(parsed)

    if canonical != value.lower():
        raise ValueError("Call UUID is not canonical")

    return canonical
