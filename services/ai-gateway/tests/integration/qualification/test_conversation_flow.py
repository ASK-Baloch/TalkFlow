from app.realtime.qualification.engine import (
    QualificationEngine,
)
from app.realtime.qualification.session import (
    QualificationSession,
)
from app.realtime.qualification.types import (
    ActionType,
    QualificationStatus,
)


def test_realistic_medicare_flow():
    engine = QualificationEngine(
        min_age=65,
        zip_length=5,
        max_clarifications_per_field=3,
    )

    session = QualificationSession(connection_id="call-001")

    turns = [
        (
            "Yes, that's fine.",
            ActionType.ASK_NAME,
        ),
        (
            "My name is Daniel Smith.",
            ActionType.ASK_AGE,
        ),
        (
            "I'm seventy two years old.",
            ActionType.ASK_PART_A,
        ),
        (
            "Yes, I have Medicare Part A.",
            ActionType.ASK_ZIP,
        ),
    ]

    for text, expected_action in turns:
        result = engine.process_transcript(
            session=session,
            text=text,
        )

        assert result.action.action_type == expected_action

    result = engine.process_transcript(
        session=session,
        text=("My ZIP code is seven five zero zero one."),
    )

    assert result.status == QualificationStatus.QUALIFIED

    assert session.lead.full_name == "Daniel Smith"

    assert session.lead.age == 72

    assert session.lead.medicare_part_a is True

    assert session.lead.medicare_part_b is None

    assert session.lead.zip_code == "75001"
