from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class SpeechMetrics:
    speech_normalization_total: int = 0
    speech_normalization_changed_total: int = 0
    speech_normalization_failures_total: int = 0

    speech_rule_zip_total: int = 0
    speech_rule_phone_total: int = 0
    speech_rule_currency_total: int = 0
    speech_rule_percentage_total: int = 0
    speech_rule_lexicon_total: int = 0

    speech_normalization_ms: deque[float] = field(
        default_factory=lambda: deque(maxlen=5000)
    )

    def average_speech_normalization_ms(self) -> float:
        if not self.speech_normalization_ms:
            return 0.0
        return sum(self.speech_normalization_ms) / len(self.speech_normalization_ms)

    def p50_speech_normalization_ms(self) -> float:
        if not self.speech_normalization_ms:
            return 0.0
        values = sorted(self.speech_normalization_ms)
        index = int(0.50 * (len(values) - 1))
        return values[index]

    def p95_speech_normalization_ms(self) -> float:
        if not self.speech_normalization_ms:
            return 0.0
        values = sorted(self.speech_normalization_ms)
        index = int(0.95 * (len(values) - 1))
        return values[index]


speech_metrics = SpeechMetrics()
