from __future__ import annotations

import re

from .lexicon import (
    PronunciationLexicon,
)
from .numbers import (
    digits_to_words,
    integer_to_words,
)
from .patterns import (
    EXCESSIVE_PUNCTUATION_PATTERN,
    MARKDOWN_PATTERN,
    PERCENT_PATTERN,
    PHONE_PATTERN,
    USD_PATTERN,
    WHITESPACE_PATTERN,
    ZIP_CONTEXT_PATTERN,
)
from .provider_adapter import (
    create_provider_adapter,
)
from .types import (
    NormalizedSpeech,
    SpeechNormalizationContext,
)


class SpeechNormalizer:
    def __init__(
        self,
        *,
        lexicon: PronunciationLexicon,
        normalize_zip_codes: bool,
        normalize_phone_numbers: bool,
        normalize_currency: bool,
        normalize_percentages: bool,
        normalize_numbers: bool,
        strip_markdown: bool,
        collapse_whitespace: bool,
        provider_adapter_enabled: bool,
        max_text_chars: int,
    ) -> None:
        self.lexicon = lexicon

        self.normalize_zip_codes = normalize_zip_codes

        self.normalize_phone_numbers = normalize_phone_numbers

        self.normalize_currency = normalize_currency

        self.normalize_percentages = normalize_percentages

        self.normalize_numbers = normalize_numbers

        self.strip_markdown = strip_markdown

        self.collapse_whitespace = collapse_whitespace

        self.provider_adapter_enabled = provider_adapter_enabled

        self.max_text_chars = max_text_chars

    def normalize(
        self,
        text: str,
        *,
        context: (SpeechNormalizationContext | None) = None,
    ) -> NormalizedSpeech:
        context = context or SpeechNormalizationContext()

        display_text = text.strip()

        if not display_text:
            return NormalizedSpeech(
                display_text="",
                tts_text="",
                changed=False,
            )

        if len(display_text) > (self.max_text_chars):
            display_text = display_text[: self.max_text_chars]

        result = display_text

        rules: list[str] = []

        if self.strip_markdown:
            updated = MARKDOWN_PATTERN.sub(
                "",
                result,
            )

            if updated != result:
                rules.append("strip_markdown")

                result = updated

        updated = EXCESSIVE_PUNCTUATION_PATTERN.sub(
            r"\1",
            result,
        )

        if updated != result:
            rules.append("collapse_punctuation")

            result = updated

        result, lexicon_rules = self.lexicon.apply(result)

        rules.extend(lexicon_rules)

        if self.normalize_zip_codes:
            result, changed = self._normalize_zip_codes(result)

            if changed:
                rules.append("zip_code")

        if self.normalize_phone_numbers:
            result, changed = self._normalize_phone_numbers(result)

            if changed:
                rules.append("phone_number")

        if self.normalize_currency:
            result, changed = self._normalize_currency(result)

            if changed:
                rules.append("currency")

        if self.normalize_percentages:
            result, changed = self._normalize_percentages(result)

            if changed:
                rules.append("percentage")

        if self.normalize_numbers:
            result, number_rules = self._normalize_contextual_numbers(
                result,
                context=context,
            )

            rules.extend(number_rules)

        if self.collapse_whitespace:
            updated = WHITESPACE_PATTERN.sub(
                " ",
                result,
            ).strip()

            if updated != result:
                rules.append("collapse_whitespace")

            result = updated

        if self.provider_adapter_enabled:
            adapter = create_provider_adapter(context.provider_name)

            updated = adapter.adapt(result)

            if updated != result:
                rules.append("provider_adapter")

            result = updated

        return NormalizedSpeech(
            display_text=display_text,
            tts_text=result,
            changed=(result != display_text),
            rules_applied=rules,
        )

    def _normalize_zip_codes(
        self,
        text: str,
    ) -> tuple[str, bool]:
        changed = False

        def replace(
            match: re.Match,
        ) -> str:
            nonlocal changed

            changed = True

            prefix = match.group(1)
            digits = match.group(2)

            return prefix + digits_to_words(digits)

        return (
            ZIP_CONTEXT_PATTERN.sub(
                replace,
                text,
            ),
            changed,
        )

    def _normalize_phone_numbers(
        self,
        text: str,
    ) -> tuple[str, bool]:
        changed = False

        def replace(
            match: re.Match,
        ) -> str:
            nonlocal changed

            changed = True

            digits = "".join(match.groups())

            return digits_to_words(digits)

        return (
            PHONE_PATTERN.sub(
                replace,
                text,
            ),
            changed,
        )

    def _normalize_currency(
        self,
        text: str,
    ) -> tuple[str, bool]:
        changed = False

        def replace(
            match: re.Match,
        ) -> str:
            nonlocal changed

            changed = True

            raw = match.group(1).replace(
                ",",
                "",
            )

            if "." in raw:
                dollars_raw, cents_raw = raw.split(
                    ".",
                    1,
                )

                dollars = int(dollars_raw)

                cents = int(
                    cents_raw.ljust(
                        2,
                        "0",
                    )[:2]
                )

                text_result = f"{integer_to_words(dollars)} dollars"

                if cents:
                    text_result += f" and {integer_to_words(cents)} cents"

                return text_result

            value = int(raw)

            return f"{integer_to_words(value)} dollars"

        return (
            USD_PATTERN.sub(
                replace,
                text,
            ),
            changed,
        )

    def _normalize_percentages(
        self,
        text: str,
    ) -> tuple[str, bool]:
        changed = False

        def replace(
            match: re.Match,
        ) -> str:
            nonlocal changed

            changed = True

            raw = match.group(1)

            if "." in raw:
                left, right = raw.split(
                    ".",
                    1,
                )

                return (
                    f"{integer_to_words(int(left))} "
                    "point "
                    f"{digits_to_words(right)} "
                    "percent"
                )

            return f"{integer_to_words(int(raw))} percent"

        return (
            PERCENT_PATTERN.sub(
                replace,
                text,
            ),
            changed,
        )

    def _normalize_contextual_numbers(
        self,
        text: str,
        *,
        context: (SpeechNormalizationContext),
    ) -> tuple[str, list[str]]:
        rules: list[str] = []

        expected_field = (context.expected_field or "").lower()

        # ZIPs have already been processed when
        # explicitly preceded by "ZIP code".
        #
        # For a response explicitly about a ZIP
        # field, convert a bare 4/5 digit value
        # digit-by-digit.
        if "zip" in expected_field:
            pattern = re.compile(r"\b(\d{4,5})\b")

            updated = pattern.sub(
                lambda match: digits_to_words(match.group(1)),
                text,
            )

            if updated != text:
                rules.append("context_zip_digits")

            return updated, rules

        # Ages should be read naturally:
        # 67 -> sixty seven
        if "age" in expected_field:
            pattern = re.compile(r"\b(\d{1,3})\b")

            def replace_age(
                match: re.Match,
            ) -> str:
                value = int(match.group(1))

                if 0 <= value <= 130:
                    return integer_to_words(value)

                return match.group(0)

            updated = pattern.sub(
                replace_age,
                text,
            )

            if updated != text:
                rules.append("context_age")

            return updated, rules

        return text, rules
