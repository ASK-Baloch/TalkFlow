from app.realtime.speech.lexicon import (
    LexiconEntry,
    PronunciationLexicon,
)


def test_case_insensitive_lexicon():
    lexicon = PronunciationLexicon(
        [
            LexiconEntry(
                source="ZIP",
                target="zip",
                case_sensitive=False,
            )
        ]
    )

    text, rules = lexicon.apply("ZIP zip Zip")

    assert text == "zip zip zip"

    assert rules
