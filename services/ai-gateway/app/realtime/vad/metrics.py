from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class VadMetrics:
    sessions_total: int = 0
    active_sessions: int = 0

    chunks_processed: int = 0

    speech_starts: int = 0
    speech_ends: int = 0

    max_speech_events: int = 0

    processing_errors: int = 0
    capacity_errors: int = 0

    inference_samples_ms: deque[float] = field(
        default_factory=lambda: deque(maxlen=5000)
    )

    def record_inference(
        self,
        milliseconds: float,
    ) -> None:
        self.inference_samples_ms.append(milliseconds)

    def inference_average_ms(self) -> float:
        if not self.inference_samples_ms:
            return 0.0

        return sum(self.inference_samples_ms) / len(self.inference_samples_ms)

    def inference_p95_ms(self) -> float:
        samples = sorted(self.inference_samples_ms)

        if not samples:
            return 0.0

        index = int(0.95 * (len(samples) - 1))

        return samples[index]


vad_metrics = VadMetrics()
