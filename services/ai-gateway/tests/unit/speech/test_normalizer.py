from app.realtime.speech.lexicon import (
    LexiconEntry,
    PronunciationLexicon,
)
from app.realtime.speech.normalizer import (
    SpeechNormalizer,
)
from app.realtime.speech.types import (
    SpeechNormalizationContext,
)


def make_normalizer():
    return SpeechNormalizer(
        lexicon=PronunciationLexicon(
            [
                LexiconEntry(
                    source="ZIP code",
                    target="zip code",
                )
            ]
        ),
        normalize_zip_codes=True,
        normalize_phone_numbers=True,
        normalize_currency=True,
        normalize_percentages=True,
        normalize_numbers=True,
        strip_markdown=True,
        collapse_whitespace=True,
        provider_adapter_enabled=True,
        max_text_chars=1000,
    )


def test_zip_code():
    normalizer = make_normalizer()

    result = normalizer.normalize("Your ZIP code is 75001.")

    assert result.tts_text == ("Your zip code is seven five zero zero one.")


def test_zip_leading_zero():
    normalizer = make_normalizer()

    result = normalizer.normalize("Your ZIP code is 07442.")

    assert "zero seven four four two" in result.tts_text


def test_age_context():
    normalizer = make_normalizer()

    result = normalizer.normalize(
        "You said you are 67 years old.",
        context=(SpeechNormalizationContext(expected_field="age")),
    )

    assert "sixty seven" in result.tts_text


def test_phone_number():
    normalizer = make_normalizer()

    result = normalizer.normalize("Call 800-555-1212.")

    assert "eight zero zero five five five one two one two" in result.tts_text


def test_percentage():
    normalizer = make_normalizer()

    result = normalizer.normalize("The value is 25%.")

    assert "twenty five percent" in result.tts_text


def test_currency():
    normalizer = make_normalizer()

    result = normalizer.normalize("The total is $25.50.")

    assert "twenty five dollars and fifty cents" in result.tts_text


def test_display_text_preserved():
    normalizer = make_normalizer()

    source = "Your ZIP code is 75001."

    result = normalizer.normalize(source)

    assert result.display_text == source
