from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import perf_counter_ns


class ResponseId(str, Enum):
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

    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONSENT_DECLINED = "consent_declined"


@dataclass(frozen=True, slots=True)
class ResponseDefinition:
    response_id: ResponseId
    text: str


@dataclass(frozen=True, slots=True)
class AudioAsset:
    response_id: ResponseId

    pcm: bytes

    sample_rate: int
    channels: int
    sample_width_bytes: int

    sample_count: int
    duration_ms: float

    sha256: str


@dataclass(slots=True)
class PlaybackRequest:
    connection_id: str

    response_id: ResponseId

    session_uuid: str | None = None

    created_ns: int = 0

    def __post_init__(self) -> None:
        if self.created_ns == 0:
            self.created_ns = perf_counter_ns()