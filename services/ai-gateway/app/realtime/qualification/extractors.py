from __future__ import annotations

"""
Important extractor limitation:

This deterministic extractor deliberately favors precision over trying to
understand absolutely everything. If unsure, extraction functions return None.
Then the state machine asks again. That is safer than hallucinating a
qualification field.
"""

import re
from dataclasses import dataclass

from .normalization import (
    normalize_name,
    normalize_text,
)
from .types import (
    ConversationState,
    ExtractedFields,
)

YES_PATTERNS = {
    "yes",
    "yeah",
    "yep",
    "yup",
    "correct",
    "right",
    "i do",
    "i have",
    "i agree",
    "i consent",
    "that's correct",
    "that is correct",
    "sure",
    "okay",
    "ok",
}

NO_PATTERNS = {
    "no",
    "nope",
    "nah",
    "i don't",
    "i do not",
    "i don't have",
    "i do not have",
    "not correct",
    "that's not correct",
    "that is not correct",
    "i decline",
    "i don't consent",
    "i do not consent",
}


DIGIT_WORDS = {
    "zero": "0",
    "oh": "0",
    "o": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


SMALL_NUMBERS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}


TENS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}


NAME_PREFIXES = (
    "my name is ",
    "this is ",
    "i am ",
    "i'm ",
)


@dataclass(slots=True)
class BooleanExtraction:
    value: bool | None

    explicit: bool


def extract_yes_no(
    text: str,
) -> BooleanExtraction:
    normalized = normalize_text(text)

    if not normalized:
        return BooleanExtraction(
            value=None,
            explicit=False,
        )

    # Check negations first because strings such as
    # "no I do not" must never be interpreted as affirmative.
    for phrase in sorted(
        NO_PATTERNS,
        key=len,
        reverse=True,
    ):
        if (
            normalized == phrase
            or normalized.startswith(phrase + " ")
            or (" " + phrase + " ") in (" " + normalized + " ")
        ):
            return BooleanExtraction(
                value=False,
                explicit=True,
            )

    for phrase in sorted(
        YES_PATTERNS,
        key=len,
        reverse=True,
    ):
        if (
            normalized == phrase
            or normalized.startswith(phrase + " ")
            or (" " + phrase + " ") in (" " + normalized + " ")
        ):
            return BooleanExtraction(
                value=True,
                explicit=True,
            )

    return BooleanExtraction(
        value=None,
        explicit=False,
    )


def _parse_number_words(
    text: str,
) -> int | None:
    normalized = normalize_text(text)

    tokens = normalized.split()

    if not tokens:
        return None

    total = 0
    current = 0
    found = False

    for token in tokens:
        if token in SMALL_NUMBERS:
            current += SMALL_NUMBERS[token]
            found = True

        elif token in TENS:
            current += TENS[token]
            found = True

        elif token == "hundred":
            if current == 0:
                current = 1

            current *= 100
            found = True

        elif token == "and":
            continue

        else:
            if found:
                break

    if not found:
        return None

    total += current

    return total


def extract_age(
    text: str,
) -> int | None:
    normalized = normalize_text(text)

    correction = re.search(
        r"\b(?:actually|sorry|correction|no)\b.*?\b(?:i am|i'm)?\s*(\d{1,3})\b",
        normalized,
    )

    if correction:
        return int(correction.group(1))

    # Prefer explicitly age-related numeric patterns.
    patterns = (
        r"\b(?:i am|i'm|age is|i am age)\s+(\d{1,3})\b",
        r"\b(\d{1,3})\s+years?\s+old\b",
        r"\bage\s+(\d{1,3})\b",
    )

    for pattern in patterns:
        match = re.search(
            pattern,
            normalized,
        )

        if match:
            return int(match.group(1))

    # If utterance is essentially just a number,
    # allow direct numeric age answers.
    direct = re.fullmatch(
        r"(?:i am\s+|i'm\s+)?(\d{1,3})(?:\s+years?\s+old)?",
        normalized,
    )

    if direct:
        return int(direct.group(1))

    # Spoken age.
    age_prefixes = (
        "i am ",
        "i'm ",
        "my age is ",
        "age is ",
    )

    candidate = normalized

    for prefix in age_prefixes:
        if candidate.startswith(prefix):
            candidate = candidate[len(prefix) :]

            candidate = candidate.replace(
                " years old",
                "",
            )

            return _parse_number_words(candidate)

    if normalized.endswith(" years old"):
        candidate = normalized[: -len(" years old")]

        return _parse_number_words(candidate)

    # Allow a short standalone spoken-number response.
    if len(normalized.split()) <= 4:
        return _parse_number_words(normalized)

    return None


def extract_zip_code(
    text: str,
) -> str | None:
    normalized = normalize_text(text)

    correction = re.search(
        r"\b(?:actually|sorry|correction)\b.*?\b(\d{5})\b",
        normalized,
    )

    if correction:
        return correction.group(1)

    # Prefer literal 5-digit form.
    match = re.search(
        r"\b(\d{5})\b",
        normalized,
    )

    if match:
        return match.group(1)

    # ZIP+4: Phase 4 keeps the primary five digits.
    match = re.search(
        r"\b(\d{5})-\d{4}\b",
        normalized,
    )

    if match:
        return match.group(1)

    tokens = normalized.split()

    digit_sequence: list[str] = []

    for token in tokens:
        if token in DIGIT_WORDS:
            digit_sequence.append(DIGIT_WORDS[token])

            if len(digit_sequence) == 5:
                return "".join(digit_sequence)

        elif token.isdigit():
            if len(token) == 1:
                digit_sequence.append(token)

                if len(digit_sequence) == 5:
                    return "".join(digit_sequence)

            else:
                digit_sequence = []

        else:
            # Words such as "zip", "code", "is", "my"
            # should not destroy a sequence.
            if token not in {
                "my",
                "zip",
                "zipcode",
                "postal",
                "code",
                "is",
                "it's",
                "its",
            }:
                if digit_sequence:
                    digit_sequence = []

    return None


def extract_name(
    text: str,
    *,
    state: ConversationState,
) -> str | None:
    normalized = normalize_text(text)

    if not normalized:
        return None

    import re

    # Strip correction words from the beginning to allow prefix matching
    correction_match = re.match(r"^(?:actually|sorry|correction|no)\s+", normalized)
    if correction_match:
        normalized = normalized[correction_match.end() :].strip()

    candidate: str | None = None

    for prefix in NAME_PREFIXES:
        if normalized.startswith(prefix):
            if prefix in ("i am ", "i'm "):
                if state != ConversationState.COLLECTING_NAME:
                    continue

            candidate = normalized[len(prefix) :].strip()

            break

    if candidate is None and state == ConversationState.COLLECTING_NAME:
        candidate = normalized

    if not candidate:
        return None

    # Strip obvious trailing clauses using regex
    candidate = re.split(r",?\s+(?:and i|i'm|i am|my age|my zip)", candidate)[0].strip()

    # Reject obvious non-name phrases containing domain semantics
    domain_words = {
        "medicare",
        "medicaid",
        "part",
        "zip",
        "age",
        "years",
        "old",
        "yes",
        "no",
        "yep",
        "nope",
    }

    words = candidate.split()
    for word in words:
        if word in domain_words:
            return None

    parts = [part for part in candidate.split() if part]

    if len(parts) < 2:
        if state != ConversationState.COLLECTING_NAME:
            return None

    if len(parts) > 5:
        return None

    for part in parts:
        cleaned = (
            part.replace(
                "'",
                "",
            )
            .replace(
                "-",
                "",
            )
            .replace(
                ".",
                "",
            )
            .replace(
                ",",
                "",
            )
        )

        if not cleaned.isalpha():
            return None

    # Do not auto-title case if it's already mixed case,
    # but the existing normalize_name does title().
    # The user tests might expect exactly what normalize_name does.
    return normalize_name(candidate)


def extract_part_a(
    text: str,
    *,
    state: ConversationState,
) -> bool | None:
    normalized = normalize_text(text)

    mentions_part_a = bool(
        re.search(
            r"\b(?:part\s+a|medicare\s+part\s+a)\b",
            normalized,
        )
    )

    if state != ConversationState.COLLECTING_PART_A and not mentions_part_a:
        return None

    if not mentions_part_a:
        mentions_part_b = bool(
            re.search(r"\b(?:part\s+b|medicare\s+part\s+b)\b", normalized)
        )
        if mentions_part_b:
            return None

    if mentions_part_a:
        if re.search(
            r"\b(?:do not|don't|dont|no|not)\b.*\bpart\s+a\b",
            normalized,
        ):
            return False

        if re.search(
            r"\b(?:have|yes|covered|got)\b.*\bpart\s+a\b",
            normalized,
        ):
            return True

    answer = extract_yes_no(normalized)

    return answer.value if answer.explicit else None


def extract_part_b(
    text: str,
    *,
    state: ConversationState,
) -> bool | None:
    normalized = normalize_text(text)

    mentions_part_b = bool(
        re.search(
            r"\b(?:part\s+b|medicare\s+part\s+b)\b",
            normalized,
        )
    )

    if state != ConversationState.COLLECTING_PART_B and not mentions_part_b:
        return None

    if not mentions_part_b:
        mentions_part_a = bool(
            re.search(r"\b(?:part\s+a|medicare\s+part\s+a)\b", normalized)
        )
        if mentions_part_a:
            return None

    if mentions_part_b:
        if re.search(
            r"\b(?:do not|don't|dont|no|not)\b.*\bpart\s+b\b",
            normalized,
        ):
            return False

        if re.search(
            r"\b(?:have|yes|covered|got)\b.*\bpart\s+b\b",
            normalized,
        ):
            return True

    answer = extract_yes_no(normalized)

    return answer.value if answer.explicit else None


def extract_fields(
    text: str,
    *,
    state: ConversationState,
) -> ExtractedFields:
    result = ExtractedFields()

    if state == ConversationState.WAITING_FOR_CONSENT:
        answer = extract_yes_no(text)

        if answer.explicit:
            result.consent = answer.value

            # Only once consent is affirmative may we
            # accept qualification information from
            # this same utterance.
            if answer.value is not True:
                return result

    result.full_name = extract_name(
        text,
        state=state,
    )

    result.age = extract_age(text)

    result.zip_code = extract_zip_code(text)

    result.medicare_part_a = extract_part_a(
        text,
        state=state,
    )

    result.medicare_part_b = extract_part_b(
        text,
        state=state,
    )

    normalized = normalize_text(text)

    if (
        "part a" in normalized
        and "part b" in normalized
        and ("both" in normalized or "have part a and part b" in normalized)
    ):
        answer = extract_yes_no(normalized)

        if answer.value is not False:
            result.medicare_part_a = True
            result.medicare_part_b = True

    return result
