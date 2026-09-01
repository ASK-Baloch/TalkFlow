from __future__ import annotations

import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")

_PUNCT_RE = re.compile(r"[^\w\s'-]")


def normalize_text(
    text: str,
) -> str:
    """
    Normalize ASR text for deterministic parsing while preserving
    apostrophes/hyphens useful for names.
    """

    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    text = text.lower().strip()

    text = _PUNCT_RE.sub(
        " ",
        text,
    )

    text = _WHITESPACE_RE.sub(
        " ",
        text,
    )

    return text.strip()


def normalize_name(
    name: str,
) -> str:
    parts = [part for part in name.strip().split() if part]

    return " ".join(_title_name_part(part) for part in parts)


def _title_name_part(
    part: str,
) -> str:
    if "'" in part:
        return "'".join(piece.capitalize() for piece in part.split("'"))

    if "-" in part:
        return "-".join(piece.capitalize() for piece in part.split("-"))

    return part.capitalize()
