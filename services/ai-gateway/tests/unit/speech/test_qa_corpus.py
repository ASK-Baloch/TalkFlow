from pathlib import Path

import pytest

from app.core.config import get_settings
from app.realtime.speech.lexicon import PronunciationLexicon
from app.realtime.speech.normalizer import SpeechNormalizer
from app.realtime.speech.types import SpeechNormalizationContext


@pytest.fixture
def normalizer():
    settings = get_settings()

    lexicon_path = Path(settings.speech_pronunciation_lexicon)
    if not lexicon_path.exists():
        # Fallback to resolving from project root if running pytest from ai-gateway
        project_root = Path(__file__).parent.parent.parent.parent.parent.parent
        lexicon_path = project_root / settings.speech_pronunciation_lexicon

    lexicon = PronunciationLexicon.from_file(str(lexicon_path))
    return SpeechNormalizer(
        lexicon=lexicon,
        normalize_zip_codes=settings.speech_normalize_zip_codes,
        normalize_phone_numbers=settings.speech_normalize_phone_numbers,
        normalize_currency=settings.speech_normalize_currency,
        normalize_percentages=settings.speech_normalize_percentages,
        normalize_numbers=settings.speech_normalize_numbers,
        strip_markdown=settings.speech_strip_markdown,
        collapse_whitespace=settings.speech_collapse_whitespace,
        provider_adapter_enabled=settings.speech_provider_adapter_enabled,
        max_text_chars=settings.speech_max_text_chars,
    )


def test_qa_corpus_zip(normalizer):
    context = SpeechNormalizationContext(expected_field="zip_code")

    # Standard ZIP
    result = normalizer.normalize("Your ZIP code is 75001.", context=context)
    assert result.tts_text == "Your zip code is seven five zero zero one."

    # Leading zero ZIP
    result = normalizer.normalize("07442", context=context)
    assert result.tts_text == "zero seven four four two"

    # Contextual inference test
    result = normalizer.normalize("My ZIP code is 12345")
    assert result.tts_text == "My zip code is one two three four five"


def test_qa_corpus_medicare_part_a(normalizer):
    result = normalizer.normalize("Do you currently have Medicare Part A?")
    assert result.tts_text == "Do you currently have Medicare Part A?"
    assert not result.changed


def test_qa_corpus_medicare_part_b(normalizer):
    result = normalizer.normalize("Do you currently have Medicare Part B?")
    assert result.tts_text == "Do you currently have Medicare Part B?"
    assert not result.changed


def test_qa_corpus_markdown_stripping(normalizer):
    result = normalizer.normalize(
        "**Medicare Part A** generally covers inpatient hospital care."
    )
    assert (
        result.tts_text == "Medicare Part A generally covers inpatient hospital care."
    )
    assert result.changed


def test_qa_corpus_numbers_with_context(normalizer):
    result = normalizer.normalize("Version 2")
    # Verify generic numbers are not globally modified unless context matches
    assert result.tts_text == "Version 2"

    result = normalizer.normalize("Part 1")
    assert result.tts_text == "Part 1"

    result = normalizer.normalize("extension 8001")
    assert result.tts_text == "extension 8001"


def test_qa_corpus_dynamic_zip_confirmation(normalizer):
    context = SpeechNormalizationContext(expected_field="zip_code")
    result = normalizer.normalize(
        "Just to confirm, your ZIP code is 75001.", context=context
    )
    assert result.display_text == "Just to confirm, your ZIP code is 75001."
    assert (
        result.tts_text == "Just to confirm, your zip code is seven five zero zero one."
    )
    assert result.changed


def test_qa_corpus_age_confirmation(normalizer):
    context = SpeechNormalizationContext(expected_field="age")
    result = normalizer.normalize(
        "Just to confirm, you are 67 years old.", context=context
    )
    assert result.tts_text == "Just to confirm, you are sixty seven years old."
    assert result.changed


def test_qa_corpus_phone_number(normalizer):
    result = normalizer.normalize("Your callback number is 800-555-1212.")
    assert (
        result.tts_text
        == "Your callback number is eight zero zero five five five one two one two."
    )
    assert result.changed


def test_qa_corpus_markdown_cleanup_from_qwen(normalizer):
    result = normalizer.normalize(
        "**Medicare Part A** generally covers inpatient hospital care."
    )
    assert (
        result.tts_text == "Medicare Part A generally covers inpatient hospital care."
    )
    assert result.changed
