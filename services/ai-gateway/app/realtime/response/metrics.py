from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class ResponseMetrics:
    stream_segments_total: int = 0

    stream_segments_dropped_stale_total: int = 0

    llm_cancellations_total: int = 0

    tts_interruptions_total: int = 0

    response_generation_invalidations_total: int = 0

    speech_end_to_first_bot_audio_ms: deque[float] = field(
        default_factory=lambda: deque(maxlen=5000)
    )

    llm_first_speakable_segment_ms: deque[float] = field(
        default_factory=lambda: deque(maxlen=5000)
    )

    def average_speech_end_to_first_bot_audio_ms(
        self,
    ) -> float:
        if not self.speech_end_to_first_bot_audio_ms:
            return 0.0

        return sum(self.speech_end_to_first_bot_audio_ms) / len(
            self.speech_end_to_first_bot_audio_ms
        )

    def p95_speech_end_to_first_bot_audio_ms(
        self,
    ) -> float:
        if not self.speech_end_to_first_bot_audio_ms:
            return 0.0

        values = sorted(self.speech_end_to_first_bot_audio_ms)

        index = int(0.95 * (len(values) - 1))

        return values[index]


response_metrics = ResponseMetrics()
