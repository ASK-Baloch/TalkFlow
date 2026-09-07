from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class TtsMetrics:
    playback_sessions_total: int = 0

    active_playbacks: int = 0

    requests_total: int = 0

    completed_total: int = 0

    playback_errors: int = 0

    queue_overflows: int = 0

    cache_errors: int = 0

    assets_missing: int = 0

    interruptions_total: int = 0

    interrupted_playbacks_total: int = 0

    flushed_requests_total: int = 0

    stale_chunks_dropped_total: int = 0

    stale_requests_dropped_total: int = 0

    first_audio_ms: deque[float] = field(default_factory=lambda: deque(maxlen=5000))

    barge_in_cancel_ms: deque[float] = field(default_factory=lambda: deque(maxlen=5000))

    def average_first_audio_ms(
        self,
    ) -> float:
        if not self.first_audio_ms:
            return 0.0

        return sum(self.first_audio_ms) / len(self.first_audio_ms)

    def p95_first_audio_ms(
        self,
    ) -> float:
        if not self.first_audio_ms:
            return 0.0

        values = sorted(self.first_audio_ms)

        index = int(0.95 * (len(values) - 1))

        return values[index]

    def average_barge_in_cancel_ms(
        self,
    ) -> float:
        if not self.barge_in_cancel_ms:
            return 0.0

        return sum(self.barge_in_cancel_ms) / len(self.barge_in_cancel_ms)

    def p95_barge_in_cancel_ms(
        self,
    ) -> float:
        if not self.barge_in_cancel_ms:
            return 0.0

        values = sorted(self.barge_in_cancel_ms)

        index = int(0.95 * (len(values) - 1))

        return values[index]


tts_metrics = TtsMetrics()
