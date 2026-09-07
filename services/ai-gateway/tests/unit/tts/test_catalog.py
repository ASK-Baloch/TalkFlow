from app.realtime.qualification.types import (
    ActionType,
)
from app.realtime.tts.catalog import (
    RESPONSES,
    response_for_action,
)
from app.realtime.tts.types import (
    ResponseId,
)


def test_all_required_responses_exist():
    required = {
        ResponseId.ASK_CONSENT,
        ResponseId.ASK_NAME,
        ResponseId.ASK_AGE,
        ResponseId.ASK_PART_A,
        ResponseId.ASK_PART_B,
        ResponseId.ASK_ZIP,
        ResponseId.CLARIFY_CONSENT,
        ResponseId.CLARIFY_NAME,
        ResponseId.CLARIFY_AGE,
        ResponseId.CLARIFY_PART_A,
        ResponseId.CLARIFY_PART_B,
        ResponseId.CLARIFY_ZIP,
        ResponseId.QUALIFIED,
        ResponseId.DISQUALIFIED,
        ResponseId.CONSENT_DECLINED,
    }

    assert required.issubset(set(RESPONSES))


def test_action_maps_to_response():
    response = response_for_action(ActionType.ASK_NAME)

    assert response is not None

    assert response.response_id == ResponseId.ASK_NAME


def test_no_action_has_no_tts():
    response = response_for_action(ActionType.NO_ACTION)

    assert response is None
