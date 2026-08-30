from dataclasses import dataclass
from enum import Enum
from time import perf_counter_ns


class TranscriptType(str, Enum):
    PARTIAL = "partial"
    FINAL = "final"


@dataclass(slots=True)
class TranscriptEvent:
    connection_id: str
    session_uuid: str | None

    utterance_id: str

    transcript_type: TranscriptType

    text: str

    revision: int

    audio_duration_ms: float

    decode_ms: float
    queue_wait_ms: float
    created_ns: int
    normalization_ms: float = 0.0

    @classmethod
    def create(
        cls,
        *,
        connection_id: str,
        session_uuid: str | None,
        utterance_id: str,
        transcript_type: TranscriptType,
        text: str,
        revision: int,
        audio_duration_ms: float,
        decode_ms: float,
        queue_wait_ms: float,
        normalization_ms: float = 0.0,
    ):
        return cls(
            connection_id=connection_id,
            session_uuid=session_uuid,
            utterance_id=utterance_id,
            transcript_type=transcript_type,
            text=text.strip(),
            revision=revision,
            audio_duration_ms=audio_duration_ms,
            decode_ms=decode_ms,
            queue_wait_ms=queue_wait_ms,
            normalization_ms=normalization_ms,
            created_ns=perf_counter_ns(),
        )
