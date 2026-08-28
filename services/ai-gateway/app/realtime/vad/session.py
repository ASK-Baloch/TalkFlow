from __future__ import annotations

import logging
from dataclasses import dataclass, field
from time import perf_counter_ns

from .audio import (
    Pcm16Chunker,
    pcm16le_to_float32,
)
from .detector import VadDetector
from .silero import SileroVadEngine
from .types import VadEvent

logger = logging.getLogger("talkflow.vad")


@dataclass(slots=True)
class VadSession:
    connection_id: str

    engine: SileroVadEngine
    chunker: Pcm16Chunker
    detector: VadDetector

    session_uuid: str | None = None

    created_ns: int = field(default_factory=perf_counter_ns)

    processed_chunks: int = 0

    def process_pcm(
        self,
        payload: bytes,
    ) -> tuple[
        list[VadEvent],
        list[float],
    ]:
        events: list[VadEvent] = []
        inference_times_ms: list[float] = []

        for pcm_chunk in self.chunker.feed(payload):
            audio = pcm16le_to_float32(pcm_chunk)

            started_ns = perf_counter_ns()

            probability = self.engine.probability(audio)

            inference_ms = (perf_counter_ns() - started_ns) / 1_000_000.0

            inference_times_ms.append(inference_ms)

            from app.core.config import get_settings
            if get_settings().vad_log_probabilities:
                logger.info(f"VAD chunk probability={probability:.3f} inference_ms={inference_ms:.2f}")

            self.processed_chunks += 1

            events.extend(self.detector.process_probability(probability))

        return (
            events,
            inference_times_ms,
        )

    def reset(self) -> None:
        self.engine.reset()
        self.chunker.reset()
        self.detector.reset()

        self.processed_chunks = 0
