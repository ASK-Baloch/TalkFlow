from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import perf_counter_ns
from uuid import uuid4


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

    generation: int

    response_id: ResponseId | None = None

    text: str | None = None

    session_uuid: str | None = None

    request_id: str = ""

    created_ns: int = 0

    speech_end_ms: float = 0.0

    def __post_init__(
        self,
    ) -> None:
        if not self.request_id:
            self.request_id = str(uuid4())

        if self.created_ns == 0:
            self.created_ns = perf_counter_ns()

        if self.response_id is None and not self.text:
            raise ValueError("PlaybackRequest requires response_id or text")
