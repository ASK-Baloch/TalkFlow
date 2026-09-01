from app.realtime.qualification.engine import (
    QualificationEngine,
)
from app.realtime.qualification.session import (
    QualificationSession,
)
from app.realtime.qualification.types import (
    ActionType,
    ConversationState,
    QualificationStatus,
)


def create_engine():
    return QualificationEngine(
        min_age=65,
        zip_length=5,
        max_clarifications_per_field=3,
    )


def create_session():
    return QualificationSession(connection_id="test-call")


def test_initial_consent_yes_advances_to_name():
    engine = create_engine()
    session = create_session()

    result = engine.process_transcript(
        session=session,
        text="Yes.",
    )

    assert session.lead.consent is True

    assert result.action.action_type == ActionType.ASK_NAME

    assert session.state == ConversationState.COLLECTING_NAME


def test_consent_no_stops_flow():
    engine = create_engine()
    session = create_session()

    result = engine.process_transcript(
        session=session,
        text="No.",
    )

    assert result.status == QualificationStatus.CONSENT_DECLINED

    assert result.action.action_type == ActionType.CONSENT_DECLINED


def test_unclear_consent_requests_clarification():
    engine = create_engine()
    session = create_session()

    result = engine.process_transcript(
        session=session,
        text="Maybe.",
    )

    assert result.action.action_type == ActionType.CLARIFY_CONSENT


def test_complete_qualified_flow():
    engine = create_engine()
    session = create_session()

    result = engine.process_transcript(
        session=session,
        text="Yes.",
    )

    assert result.action.action_type == ActionType.ASK_NAME

    result = engine.process_transcript(
        session=session,
        text="Daniel Smith.",
    )

    assert result.action.action_type == ActionType.ASK_AGE

    result = engine.process_transcript(
        session=session,
        text="I am 70 years old.",
    )

    assert result.action.action_type == ActionType.ASK_PART_A

    result = engine.process_transcript(
        session=session,
        text="Yes, I have Part A.",
    )

    assert result.action.action_type == ActionType.ASK_ZIP

    result = engine.process_transcript(
        session=session,
        text="75001.",
    )

    assert result.status == QualificationStatus.QUALIFIED

    assert result.action.action_type == ActionType.QUALIFIED


def test_age_disqualifies_immediately():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(
        session=session,
        text="Yes.",
    )

    engine.process_transcript(
        session=session,
        text="Daniel Smith.",
    )

    result = engine.process_transcript(
        session=session,
        text="I am 61.",
    )

    assert result.status == QualificationStatus.DISQUALIFIED

    assert result.action.reason == "age_below_minimum"


def test_out_of_order_fields_are_preserved():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(
        session=session,
        text="Yes.",
    )

    result = engine.process_transcript(
        session=session,
        text=(
            "My name is Daniel Smith and I am 70 years old and my ZIP code is 75001."
        ),
    )

    assert session.lead.full_name == "Daniel Smith"

    assert session.lead.age == 70

    assert session.lead.zip_code == "75001"

    assert result.action.action_type == ActionType.ASK_PART_A


def test_part_a_no_asks_part_b():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(
        session=session,
        text="Yes.",
    )

    engine.process_transcript(
        session=session,
        text="Daniel Smith.",
    )

    engine.process_transcript(
        session=session,
        text="70.",
    )

    result = engine.process_transcript(
        session=session,
        text="No, I do not have Part A.",
    )

    assert result.action.action_type == ActionType.ASK_PART_B


def test_invalid_name_clarifies():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(
        session=session,
        text="Yes.",
    )

    result = engine.process_transcript(
        session=session,
        text="age 67",
    )

    assert result.action.action_type == ActionType.CLARIFY_NAME


def test_name_extraction_preserves_next_state():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(
        session=session,
        text="Yes.",
    )

    result = engine.process_transcript(
        session=session,
        text="My name is Alex.",
    )

    assert session.lead.full_name == "Alex"
    assert result.action.action_type == ActionType.ASK_AGE
    assert session.state == ConversationState.COLLECTING_AGE


def test_existing_field_not_overwritten():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    engine.process_transcript(session=session, text="My name is Alex.")
    engine.process_transcript(session=session, text="67.")
    engine.process_transcript(session=session, text="Yes I have Part A.")

    result = engine.process_transcript(
        session=session,
        text="I have Part B.",
    )

    assert session.lead.full_name == "Alex"
    assert session.lead.medicare_part_b is True


def test_age_does_not_overwrite_name():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    result = engine.process_transcript(session=session, text="My age is 67.")

    assert session.lead.age == 67
    assert session.lead.full_name is None


def test_zip_does_not_overwrite_name():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    result = engine.process_transcript(session=session, text="My ZIP code is 74423.")

    assert session.lead.zip_code == "74423"
    assert session.lead.full_name is None


def test_part_a_does_not_overwrite_name():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    result = engine.process_transcript(session=session, text="I have Medicare Part A.")

    assert session.lead.medicare_part_a is True
    assert session.lead.full_name is None


def test_negation_preserved():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    engine.process_transcript(session=session, text="Alex.")
    engine.process_transcript(session=session, text="67.")
    engine.process_transcript(session=session, text="Yes.")

    result = engine.process_transcript(session=session, text="No, I don't have Part B.")

    assert session.lead.medicare_part_b is False


def test_global_volunteered_fields():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    result = engine.process_transcript(
        session=session,
        text="My name is Alex, I'm 67, and my ZIP code is 74423.",
    )

    assert session.lead.full_name == "Alex"
    assert session.lead.age == 67
    assert session.lead.zip_code == "74423"
    assert result.action.action_type == ActionType.ASK_PART_A


def test_correction_overwrites_field():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    engine.process_transcript(session=session, text="Alex.")
    
    result = engine.process_transcript(
        session=session, 
        text="Actually my name is Daniel Smith."
    )

    assert session.lead.full_name == "Daniel Smith"


def test_part_b_does_not_overwrite_name_when_existing():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes.")
    engine.process_transcript(session=session, text="Alex.")
    
    result = engine.process_transcript(
        session=session, 
        text="I have Part B."
    )

    assert session.lead.full_name == "Alex"
    assert session.lead.medicare_part_b is True


def test_observed_production_sequence():
    engine = create_engine()
    session = create_session()

    engine.process_transcript(session=session, text="Yes, continue.")
    engine.process_transcript(session=session, text="My name is Alex.")
    engine.process_transcript(session=session, text="My age is 67.")
    engine.process_transcript(session=session, text="My zip code is 74423.")
    
    result = engine.process_transcript(session=session, text="I have Part B.")

    assert session.lead.consent is True
    assert session.lead.full_name == "Alex"
    assert session.lead.age == 67
    assert session.lead.medicare_part_a is None
    assert session.lead.medicare_part_b is True
    assert session.lead.zip_code == "74423"

    assert session.state == ConversationState.QUALIFIED
    assert session.status == QualificationStatus.QUALIFIED
    assert session.transcript_count == 5

def test_medicare_part_a_true_skips_part_b():
    engine = create_engine()
    session = create_session()
    
    session.lead.consent = True
    session.lead.full_name = 'Alex'
    session.lead.age = 67
    
    # State should become COLLECTING_PART_A
    engine.process_transcript(session=session, text='Yes I consent')
    
    result = engine.process_transcript(session=session, text='I have Part A')
    
    assert session.lead.medicare_part_a is True
    assert session.lead.medicare_part_b is None
    assert result.action.action_type == ActionType.ASK_ZIP

def test_medicare_part_a_false_asks_part_b():
    engine = create_engine()
    session = create_session()
    
    session.lead.consent = True
    session.lead.full_name = 'Alex'
    session.lead.age = 67
    
    engine.process_transcript(session=session, text='Yes I consent')
    
    result = engine.process_transcript(session=session, text='I do not have Part A')
    
    assert session.lead.medicare_part_a is False
    assert result.action.action_type == ActionType.ASK_PART_B

def test_medicare_part_a_false_part_b_true_satisfies():
    engine = create_engine()
    session = create_session()
    
    session.lead.consent = True
    session.lead.full_name = 'Alex'
    session.lead.age = 67
    session.lead.zip_code = '74423'
    
    engine.process_transcript(session=session, text='Yes I consent')
    engine.process_transcript(session=session, text='No Part A')
    
    assert session.state == ConversationState.COLLECTING_PART_B
    result = engine.process_transcript(session=session, text='I have Part B')
    
    assert session.lead.medicare_part_a is False
    assert session.lead.medicare_part_b is True
    assert session.state == ConversationState.QUALIFIED

def test_medicare_part_a_null_part_b_true_satisfies():
    engine = create_engine()
    session = create_session()
    
    session.lead.consent = True
    session.lead.full_name = 'Alex'
    session.lead.age = 67
    session.lead.zip_code = '74423'
    
    engine.process_transcript(session=session, text='Yes I consent')
    
    result = engine.process_transcript(session=session, text='I have Part B')
    
    assert session.lead.medicare_part_a is None
    assert session.lead.medicare_part_b is True
    assert session.state == ConversationState.QUALIFIED

def test_medicare_both_false_disqualifies():
    engine = create_engine()
    session = create_session()
    
    session.lead.consent = True
    session.lead.full_name = 'Alex'
    session.lead.age = 67
    session.lead.zip_code = '74423'
    
    engine.process_transcript(session=session, text='Yes I consent')
    engine.process_transcript(session=session, text='No Part A')
    result = engine.process_transcript(session=session, text='No Part B')
    
    assert session.lead.medicare_part_a is False
    assert session.lead.medicare_part_b is False
    assert session.state == ConversationState.DISQUALIFIED

def test_medicare_both_true_satisfies():
    engine = create_engine()
    session = create_session()
    
    session.lead.consent = True
    session.lead.full_name = 'Alex'
    session.lead.age = 67
    session.lead.zip_code = '74423'
    
    engine.process_transcript(session=session, text='Yes I consent')
    
    result = engine.process_transcript(session=session, text='I have Part A and Part B')
    
    assert session.lead.medicare_part_a is True
    assert session.lead.medicare_part_b is True
    assert session.state == ConversationState.QUALIFIED

