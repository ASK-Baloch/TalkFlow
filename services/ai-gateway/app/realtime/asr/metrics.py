from collections import deque
from dataclasses import dataclass, field


@dataclass
class AsrMetrics:
    sessions_total: int = 0
    active_sessions: int = 0

    jobs_submitted: int = 0

    partials_emitted: int = 0
    finals_emitted: int = 0

    stale_partials_dropped: int = 0
    queue_overflows: int = 0
    decode_errors: int = 0

    partial_decode_ms: deque = field(default_factory=lambda: deque(maxlen=5000))
    final_decode_ms: deque = field(default_factory=lambda: deque(maxlen=5000))
    first_partial_latency_ms: deque = field(default_factory=lambda: deque(maxlen=5000))

    def partial_decode_average_ms(self) -> float:
        if not self.partial_decode_ms:
            return 0.0
        return sum(self.partial_decode_ms) / len(self.partial_decode_ms)

    def partial_decode_p95_ms(self) -> float:
        if not self.partial_decode_ms:
            return 0.0
        import numpy as np

        return float(np.percentile(self.partial_decode_ms, 95))

    def final_decode_average_ms(self) -> float:
        if not self.final_decode_ms:
            return 0.0
        return sum(self.final_decode_ms) / len(self.final_decode_ms)

    def final_decode_p95_ms(self) -> float:
        if not self.final_decode_ms:
            return 0.0
        import numpy as np

        return float(np.percentile(self.final_decode_ms, 95))


asr_metrics = AsrMetrics()
