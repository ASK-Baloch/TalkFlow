from dataclasses import dataclass
from enum import Enum
from time import monotonic_ns


class VadState(str, Enum):
    SILENCE = "silence"
    SPEAKING = "speaking"
    PENDING_END = "pending_end"


class VadEventType(str, Enum):
    SPEECH_START = "speech_start"
    SPEECH_END = "speech_end"
    MAX_SPEECH_REACHED = "max_speech_reached"
    SPEECH_PENDING_END = "speech_pending_end"
    SPEECH_RESUMED = "speech_resumed"


@dataclass(slots=True)
class VadEvent:
    event_type: VadEventType
    sample_index: int
    probability: float
    detection_delay_ms: float
    created_ns: int

    @classmethod
    def create(
        cls,
        *,
        event_type: VadEventType,
        sample_index: int,
        probability: float,
        detection_delay_ms: float,
    ) -> "VadEvent":
        return cls(
            event_type=event_type,
            sample_index=sample_index,
            probability=probability,
            detection_delay_ms=detection_delay_ms,
            created_ns=monotonic_ns(),
        )
