from app.realtime.qualification.extractors import (
    extract_age,
    extract_fields,
    extract_name,
    extract_part_a,
    extract_part_b,
    extract_yes_no,
    extract_zip_code,
)
from app.realtime.qualification.types import (
    ConversationState,
)


def test_yes():
    result = extract_yes_no("Yes, I do.")

    assert result.value is True
    assert result.explicit is True


def test_no():
    result = extract_yes_no("No, I do not.")

    assert result.value is False
    assert result.explicit is True


def test_unclear_boolean():
    result = extract_yes_no("Maybe.")

    assert result.value is None


def test_numeric_age():
    assert extract_age("I'm 67 years old.") == 67


def test_spoken_age():
    assert extract_age("I am seventy two years old") == 72


def test_name():
    assert (
        extract_name(
            "My name is Daniel Smith",
            state=(ConversationState.COLLECTING_NAME),
        )
        == "Daniel Smith"
    )


def test_direct_name_when_expected():
    assert (
        extract_name(
            "Daniel Smith",
            state=(ConversationState.COLLECTING_NAME),
        )
        == "Daniel Smith"
    )


def test_single_word_not_accepted_as_full_name():
    assert (
        extract_name(
            "Daniel",
            state=(ConversationState.COLLECTING_NAME),
        )
        is None
    )


def test_numeric_zip():
    assert extract_zip_code("My ZIP code is 75001.") == "75001"


def test_spoken_zip():
    assert extract_zip_code("My zip code is seven five zero zero one") == "75001"


def test_part_a_yes():
    assert (
        extract_part_a(
            "Yes, I have Medicare Part A",
            state=(ConversationState.COLLECTING_PART_A),
        )
        is True
    )


def test_part_a_no():
    assert (
        extract_part_a(
            "No, I do not have Part A",
            state=(ConversationState.COLLECTING_PART_A),
        )
        is False
    )


def test_part_b_yes():
    assert (
        extract_part_b(
            "Yes, I have Medicare Part B",
            state=(ConversationState.COLLECTING_PART_B),
        )
        is True
    )


def test_consent_gate_rejects_other_fields_on_no():
    fields = extract_fields(
        ("No, my name is Daniel Smith and I'm 72."),
        state=(ConversationState.WAITING_FOR_CONSENT),
    )

    assert fields.consent is False
    assert fields.full_name is None
    assert fields.age is None


def test_consent_yes_allows_same_utterance_fields():
    fields = extract_fields(
        ("Yes, my name is Daniel Smith and I'm 72."),
        state=(ConversationState.WAITING_FOR_CONSENT),
    )

    assert fields.consent is True
    assert fields.age == 72


def test_both_part_a_and_part_b():
    fields = extract_fields(
        "Yes I have both Medicare Part A and Part B.",
        state=ConversationState.COLLECTING_PART_A,
    )

    assert fields.medicare_part_a is True
    assert fields.medicare_part_b is True


def test_age_correction():
    assert extract_age("Sorry, I'm 68, not 67.") == 68
    assert extract_age("No actually I am 72") == 72


def test_zip_correction():
    assert extract_zip_code("Actually my ZIP is 75002.") == "75002"
    assert extract_zip_code("Sorry correction 12345") == "12345"
