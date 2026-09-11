from __future__ import annotations

import logging

from .normalizer import (
    SpeechNormalizer,
)
from .types import (
    NormalizedSpeech,
    SpeechNormalizationContext,
)

logger = logging.getLogger("talkflow.speech")


class SpeechNormalizationService:
    def __init__(
        self,
        *,
        normalizer: SpeechNormalizer,
        enabled: bool,
        log_normalization: bool,
    ) -> None:
        self.normalizer = normalizer

        self.enabled = enabled

        self.log_normalization = log_normalization

    def normalize(
        self,
        text: str,
        *,
        context: (SpeechNormalizationContext | None) = None,
    ) -> NormalizedSpeech:
        if not self.enabled:
            return NormalizedSpeech(
                display_text=text,
                tts_text=text,
                changed=False,
            )

        from time import perf_counter

        from .metrics import speech_metrics

        start_time = perf_counter()

        try:
            result = self.normalizer.normalize(
                text,
                context=context,
            )
        except Exception:
            logger.exception("Speech normalization failed")
            speech_metrics.speech_normalization_failures_total += 1
            result = NormalizedSpeech(
                display_text=text,
                tts_text=text,
                changed=False,
            )

        elapsed_ms = (perf_counter() - start_time) * 1000.0

        speech_metrics.speech_normalization_ms.append(elapsed_ms)
        speech_metrics.speech_normalization_total += 1

        if result.changed:
            speech_metrics.speech_normalization_changed_total += 1
            for rule in result.rules_applied:
                if "zip" in rule.lower():
                    speech_metrics.speech_rule_zip_total += 1
                elif "phone" in rule.lower():
                    speech_metrics.speech_rule_phone_total += 1
                elif "currency" in rule.lower():
                    speech_metrics.speech_rule_currency_total += 1
                elif "percentage" in rule.lower() or "percent" in rule.lower():
                    speech_metrics.speech_rule_percentage_total += 1
                elif "lexicon" in rule.lower():
                    speech_metrics.speech_rule_lexicon_total += 1

        if self.log_normalization and result.changed:
            logger.debug(
                "Speech normalization applied rules=%s",
                result.rules_applied,
            )

        return result
