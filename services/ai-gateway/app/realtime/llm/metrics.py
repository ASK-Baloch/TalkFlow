from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class LLMMetrics:
    requests_total: int = 0

    completed_total: int = 0

    failures_total: int = 0

    timeouts_total: int = 0

    empty_responses_total: int = 0

    fallback_skipped_total: int = 0

    latency_ms: deque[float] = field(default_factory=lambda: deque(maxlen=5000))

    def average_latency_ms(
        self,
    ) -> float:
        if not self.latency_ms:
            return 0.0

        return sum(self.latency_ms) / len(self.latency_ms)

    def p95_latency_ms(
        self,
    ) -> float:
        if not self.latency_ms:
            return 0.0

        values = sorted(self.latency_ms)

        index = int(0.95 * (len(values) - 1))

        return values[index]


llm_metrics = LLMMetrics()
