from dataclasses import dataclass
from enum import Enum
from time import perf_counter_ns


class TranscriptType(str, Enum):
    PARTIAL = "partial"
    FINAL_TENTATIVE = "final_tentative"
    FINAL = "final"


@dataclass(slots=True)
class TranscriptEvent:
    connection_id: str
    session_uuid: str | None
    utterance_id: str
    transcript_type: TranscriptType
    revision: int
    raw_text: str
    normalized_text: str
    text: str
    audio_duration_ms: float
    decode_ms: float
    queue_wait_ms: float
    normalization_ms: float
    created_ns: int

    # Additional detailed latency fields
    job_created_ns: int = 0
    worker_start_ns: int = 0
    decode_start_ns: int = 0
    decode_done_ns: int = 0
    emit_ns: int = 0
    acoustic_end_ns: int = 0

    @classmethod
    def create(
        cls,
        *,
        connection_id: str,
        session_uuid: str | None,
        utterance_id: str,
        transcript_type: TranscriptType,
        raw_text: str,
        normalized_text: str,
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
            raw_text=raw_text.strip(),
            normalized_text=normalized_text.strip(),
            text=normalized_text.strip(),
            revision=revision,
            audio_duration_ms=audio_duration_ms,
            decode_ms=decode_ms,
            queue_wait_ms=queue_wait_ms,
            normalization_ms=normalization_ms,
            created_ns=perf_counter_ns(),
        )
