from __future__ import annotations

from app.realtime.qualification.types import ActionType

from .types import (
    ResponseDefinition,
    ResponseId,
)

RESPONSES: dict[
    ResponseId,
    ResponseDefinition,
] = {
    ResponseId.ASK_CONSENT: ResponseDefinition(
        response_id=ResponseId.ASK_CONSENT,
        text=(
            "Before we continue, may I ask you a few questions "
            "to see whether you may qualify?"
        ),
    ),

    ResponseId.ASK_NAME: ResponseDefinition(
        response_id=ResponseId.ASK_NAME,
        text="Great. May I have your full name?",
    ),

    ResponseId.ASK_AGE: ResponseDefinition(
        response_id=ResponseId.ASK_AGE,
        text="Thank you. How old are you?",
    ),

    ResponseId.ASK_PART_A: ResponseDefinition(
        response_id=ResponseId.ASK_PART_A,
        text="Do you currently have Medicare Part A?",
    ),

    ResponseId.ASK_PART_B: ResponseDefinition(
        response_id=ResponseId.ASK_PART_B,
        text="And do you currently have Medicare Part B?",
    ),

    ResponseId.ASK_ZIP: ResponseDefinition(
        response_id=ResponseId.ASK_ZIP,
        text="What is your five digit ZIP code?",
    ),

    ResponseId.CLARIFY_CONSENT: ResponseDefinition(
        response_id=ResponseId.CLARIFY_CONSENT,
        text=(
            "Sorry, I didn't catch that. "
            "Is it okay if I ask you a few qualification questions?"
        ),
    ),

    ResponseId.CLARIFY_NAME: ResponseDefinition(
        response_id=ResponseId.CLARIFY_NAME,
        text=(
            "Sorry, could you please tell me your first and last name?"
        ),
    ),

    ResponseId.CLARIFY_AGE: ResponseDefinition(
        response_id=ResponseId.CLARIFY_AGE,
        text="Sorry, could you tell me your age in years?",
    ),

    ResponseId.CLARIFY_PART_A: ResponseDefinition(
        response_id=ResponseId.CLARIFY_PART_A,
        text=(
            "Sorry, I need to confirm this. "
            "Do you currently have Medicare Part A?"
        ),
    ),

    ResponseId.CLARIFY_PART_B: ResponseDefinition(
        response_id=ResponseId.CLARIFY_PART_B,
        text=(
            "Sorry, I need to confirm this. "
            "Do you currently have Medicare Part B?"
        ),
    ),

    ResponseId.CLARIFY_ZIP: ResponseDefinition(
        response_id=ResponseId.CLARIFY_ZIP,
        text=(
            "Sorry, could you repeat your five digit ZIP code, "
            "one digit at a time?"
        ),
    ),

    ResponseId.QUALIFIED: ResponseDefinition(
        response_id=ResponseId.QUALIFIED,
        text=(
            "Thank you. I have the information I need."
        ),
    ),

    ResponseId.DISQUALIFIED: ResponseDefinition(
        response_id=ResponseId.DISQUALIFIED,
        text=(
            "Thank you for your time. "
            "Based on the information provided, "
            "we are unable to continue with this qualification."
        ),
    ),

    ResponseId.CONSENT_DECLINED: ResponseDefinition(
        response_id=ResponseId.CONSENT_DECLINED,
        text=(
            "No problem. Thank you for your time."
        ),
    ),
}


ACTION_RESPONSE_MAP: dict[
    ActionType,
    ResponseId,
] = {
    ActionType.ASK_CONSENT:
        ResponseId.ASK_CONSENT,

    ActionType.ASK_NAME:
        ResponseId.ASK_NAME,

    ActionType.ASK_AGE:
        ResponseId.ASK_AGE,

    ActionType.ASK_PART_A:
        ResponseId.ASK_PART_A,

    ActionType.ASK_PART_B:
        ResponseId.ASK_PART_B,

    ActionType.ASK_ZIP:
        ResponseId.ASK_ZIP,

    ActionType.CLARIFY_CONSENT:
        ResponseId.CLARIFY_CONSENT,

    ActionType.CLARIFY_NAME:
        ResponseId.CLARIFY_NAME,

    ActionType.CLARIFY_AGE:
        ResponseId.CLARIFY_AGE,

    ActionType.CLARIFY_PART_A:
        ResponseId.CLARIFY_PART_A,

    ActionType.CLARIFY_PART_B:
        ResponseId.CLARIFY_PART_B,

    ActionType.CLARIFY_ZIP:
        ResponseId.CLARIFY_ZIP,

    ActionType.QUALIFIED:
        ResponseId.QUALIFIED,

    ActionType.DISQUALIFIED:
        ResponseId.DISQUALIFIED,

    ActionType.CONSENT_DECLINED:
        ResponseId.CONSENT_DECLINED,
}


def response_for_action(
    action_type: ActionType,
) -> ResponseDefinition | None:
    response_id = ACTION_RESPONSE_MAP.get(
        action_type
    )

    if response_id is None:
        return None

    return RESPONSES[response_id]