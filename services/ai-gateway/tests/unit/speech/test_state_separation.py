from copy import deepcopy

from app.realtime.speech.lexicon import (
    PronunciationLexicon,
)
from app.realtime.speech.normalizer import (
    SpeechNormalizer,
)


def test_normalization_does_not_mutate_business_state():
    state = {
        "zip_code": "75001",
        "age": 67,
        "part_a": True,
    }

    original = deepcopy(state)

    normalizer = SpeechNormalizer(
        lexicon=PronunciationLexicon([]),
        normalize_zip_codes=True,
        normalize_phone_numbers=True,
        normalize_currency=True,
        normalize_percentages=True,
        normalize_numbers=True,
        strip_markdown=True,
        collapse_whitespace=True,
        provider_adapter_enabled=False,
        max_text_chars=1000,
    )

    normalizer.normalize("Your ZIP code is 75001.")

    assert state == original
