from __future__ import annotations

import re

ZIP_CONTEXT_PATTERN = re.compile(
    r"\b((?:zip|ZIP|Zip)\s*(?:code)?\s*"
    r"(?:is\s+)?[:#-]?\s*)(\d{4,5})(?:-\d{4})?\b",
    re.IGNORECASE,
)


PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?1[\s.-]?)?"
    r"\(?(\d{3})\)?[\s.-]?"
    r"(\d{3})[\s.-]?"
    r"(\d{4})"
    r"(?!\d)"
)


PERCENT_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?)%")


USD_PATTERN = re.compile(r"\$(\d+(?:,\d{3})*(?:\.\d{1,2})?)")


PLAIN_INTEGER_PATTERN = re.compile(r"\b\d+\b")


EXCESSIVE_PUNCTUATION_PATTERN = re.compile(r"([!?.,])\1+")


WHITESPACE_PATTERN = re.compile(r"\s+")


MARKDOWN_PATTERN = re.compile(r"[*_`#>{}\[\]]")
