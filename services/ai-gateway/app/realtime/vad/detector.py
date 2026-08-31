from __future__ import annotations

from dataclasses import dataclass

from .types import (
    VadEvent,
    VadEventType,
    VadState,
)


@dataclass(slots=True)
class VadDetectorConfig:
    sample_rate: int
    chunk_samples: int

    threshold: float
    neg_threshold: float

    min_speech_ms: int
    min_silence_ms: int

    max_speech_seconds: int


class VadDetector:
    """
    Stateful TalkFlow endpoint detector.

    Silero produces a probability for every audio chunk.
    This class converts those probabilities into stable call events.
    """

    def __init__(
        self,
        config: VadDetectorConfig,
    ) -> None:
        self.config = config

        self._chunk_ms = config.chunk_samples / config.sample_rate * 1000.0

        self.reset()

    def reset(self) -> None:
        self.state = VadState.SILENCE

        self.total_samples = 0

        self._speech_candidate_samples = 0
        self._silence_candidate_samples = 0

        self._speech_started_sample: int | None = None

    @property
    def speaking(self) -> bool:
        return self.state in (VadState.SPEAKING, VadState.PENDING_END)

    def process_probability(
        self,
        probability: float,
    ) -> list[VadEvent]:
        events: list[VadEvent] = []

        chunk_samples = self.config.chunk_samples

        chunk_start = self.total_samples
        chunk_end = chunk_start + chunk_samples

        self.total_samples = chunk_end

        if self.state == VadState.SILENCE:
            events.extend(
                self._process_silence(
                    probability=probability,
                    chunk_start=chunk_start,
                )
            )

        elif self.state == VadState.SPEAKING:
            events.extend(
                self._process_speaking(
                    probability=probability,
                    chunk_end=chunk_end,
                )
            )
            
        elif self.state == VadState.PENDING_END:
            events.extend(
                self._process_pending_end(
                    probability=probability,
                    chunk_end=chunk_end,
                )
            )

        return events

    def _process_silence(
        self,
        *,
        probability: float,
        chunk_start: int,
    ) -> list[VadEvent]:
        if probability >= self.config.threshold:
            if self._speech_candidate_samples == 0:
                candidate_start = chunk_start
            else:
                candidate_start = chunk_start - self._speech_candidate_samples

            self._speech_candidate_samples += self.config.chunk_samples

            candidate_ms = (
                self._speech_candidate_samples / self.config.sample_rate * 1000.0
            )

            if candidate_ms >= self.config.min_speech_ms:
                self.state = VadState.SPEAKING

                self._speech_started_sample = candidate_start
                self._speech_candidate_samples = 0
                self._silence_candidate_samples = 0

                return [
                    VadEvent.create(
                        event_type=VadEventType.SPEECH_START,
                        sample_index=candidate_start,
                        probability=probability,
                        detection_delay_ms=candidate_ms,
                    )
                ]

        else:
            self._speech_candidate_samples = 0

        return []

    def _process_speaking(
        self,
        *,
        probability: float,
        chunk_end: int,
    ) -> list[VadEvent]:
        if self._speech_started_sample is not None:
            speech_samples = chunk_end - self._speech_started_sample

            max_samples = self.config.sample_rate * self.config.max_speech_seconds

            if speech_samples >= max_samples:
                event = VadEvent.create(
                    event_type=VadEventType.MAX_SPEECH_REACHED,
                    sample_index=chunk_end,
                    probability=probability,
                    detection_delay_ms=0.0,
                )

                self._return_to_silence()
                return [event]

        if probability < self.config.neg_threshold:
            # We instantly enter PENDING_END upon dropping below negative threshold
            self.state = VadState.PENDING_END
            self._silence_candidate_samples = self.config.chunk_samples
            
            return [
                VadEvent.create(
                    event_type=VadEventType.SPEECH_PENDING_END,
                    sample_index=chunk_end - self.config.chunk_samples,
                    probability=probability,
                    detection_delay_ms=0.0,
                )
            ]

        return []
        
    def _process_pending_end(
        self,
        *,
        probability: float,
        chunk_end: int,
    ) -> list[VadEvent]:
        if self._speech_started_sample is not None:
            speech_samples = chunk_end - self._speech_started_sample
            max_samples = self.config.sample_rate * self.config.max_speech_seconds

            if speech_samples >= max_samples:
                event = VadEvent.create(
                    event_type=VadEventType.MAX_SPEECH_REACHED,
                    sample_index=chunk_end,
                    probability=probability,
                    detection_delay_ms=0.0,
                )
                self._return_to_silence()
                return [event]
                
        if probability >= self.config.threshold:
            # Speech has resumed before the hangover expired
            self.state = VadState.SPEAKING
            
            silence_ms = (
                self._silence_candidate_samples / self.config.sample_rate * 1000.0
            )
            
            self._silence_candidate_samples = 0
            
            return [
                VadEvent.create(
                    event_type=VadEventType.SPEECH_RESUMED,
                    sample_index=chunk_end,
                    probability=probability,
                    detection_delay_ms=silence_ms,
                )
            ]
            
        else:
            self._silence_candidate_samples += self.config.chunk_samples

            silence_ms = (
                self._silence_candidate_samples / self.config.sample_rate * 1000.0
            )

            if silence_ms >= self.config.min_silence_ms:
                end_sample = chunk_end - self._silence_candidate_samples

                event = VadEvent.create(
                    event_type=VadEventType.SPEECH_END,
                    sample_index=end_sample,
                    probability=probability,
                    detection_delay_ms=silence_ms,
                )

                self._return_to_silence()
                return [event]
                
        return []

    def _return_to_silence(self) -> None:
        self.state = VadState.SILENCE

        self._speech_candidate_samples = 0
        self._silence_candidate_samples = 0
        self._speech_started_sample = None
