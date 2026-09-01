from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter_ns
from typing import Any


class ConversationState(str, Enum):
    WAITING_FOR_CONSENT = "waiting_for_consent"

    COLLECTING_NAME = "collecting_name"
    COLLECTING_AGE = "collecting_age"
    COLLECTING_PART_A = "collecting_part_a"
    COLLECTING_PART_B = "collecting_part_b"
    COLLECTING_ZIP = "collecting_zip"

    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONSENT_DECLINED = "consent_declined"

    COMPLETE = "complete"


class QualificationStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONSENT_DECLINED = "consent_declined"


class ActionType(str, Enum):
    ASK_CONSENT = "ask_consent"

    ASK_NAME = "ask_name"
    ASK_AGE = "ask_age"
    ASK_PART_A = "ask_part_a"
    ASK_PART_B = "ask_part_b"
    ASK_ZIP = "ask_zip"

    CLARIFY_CONSENT = "clarify_consent"
    CLARIFY_NAME = "clarify_name"
    CLARIFY_AGE = "clarify_age"
    CLARIFY_PART_A = "clarify_part_a"
    CLARIFY_PART_B = "clarify_part_b"
    CLARIFY_ZIP = "clarify_zip"

    CONFIRM_NAME = "confirm_name"
    CONFIRM_AGE = "confirm_age"
    CONFIRM_ZIP = "confirm_zip"

    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONSENT_DECLINED = "consent_declined"

    NO_ACTION = "no_action"


class FieldName(str, Enum):
    CONSENT = "consent"
    FULL_NAME = "full_name"
    AGE = "age"
    MEDICARE_PART_A = "medicare_part_a"
    MEDICARE_PART_B = "medicare_part_b"
    ZIP_CODE = "zip_code"


@dataclass(slots=True)
class LeadData:
    consent: bool | None = None

    full_name: str | None = None
    age: int | None = None

    medicare_part_a: bool | None = None
    medicare_part_b: bool | None = None

    zip_code: str | None = None


@dataclass(slots=True)
class ExtractedFields:
    consent: bool | None = None

    full_name: str | None = None
    age: int | None = None

    medicare_part_a: bool | None = None
    medicare_part_b: bool | None = None

    zip_code: str | None = None


@dataclass(slots=True)
class ConversationAction:
    action_type: ActionType

    state: ConversationState

    qualification_status: QualificationStatus

    reason: str | None = None

    expected_field: FieldName | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    created_ns: int = field(default_factory=perf_counter_ns)


@dataclass(slots=True)
class QualificationResult:
    state: ConversationState

    status: QualificationStatus

    lead: LeadData

    action: ConversationAction

    fields_updated: list[FieldName] = field(default_factory=list)
