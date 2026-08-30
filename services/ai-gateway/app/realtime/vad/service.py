from __future__ import annotations

import logging

from app.core.config import get_settings

from .audio import Pcm16Chunker
from .detector import (
    VadDetector,
    VadDetectorConfig,
)
from .metrics import vad_metrics
from .pool import (
    SileroVadPool,
    VadCapacityError,
)
from .session import VadSession
from .types import VadEventType

logger = logging.getLogger("talkflow.vad")


class VadService:
    def __init__(self) -> None:
        settings = get_settings()

        self.enabled = settings.vad_enabled

        self.log_probabilities = settings.vad_log_probabilities

        self._settings = settings

        self.pool = SileroVadPool(
            sample_rate=settings.vad_sample_rate,
            use_onnx=settings.vad_use_onnx,
            size=settings.vad_pool_size,
            acquire_timeout_ms=(settings.vad_pool_acquire_timeout_ms),
        )

        self._sessions: dict[
            str,
            VadSession,
        ] = {}

        self._leases = {}

    async def start(self) -> None:
        if not self.enabled:
            logger.info("VAD disabled")
            return

        await self.pool.start()

        logger.info(
            (
                "Silero VAD ready "
                "sample_rate=%s "
                "pool_size=%s "
                "threshold=%s "
                "neg_threshold=%s "
                "min_speech_ms=%s "
                "min_silence_ms=%s"
            ),
            self._settings.vad_sample_rate,
            self._settings.vad_pool_size,
            self._settings.vad_threshold,
            self._settings.vad_neg_threshold,
            self._settings.vad_min_speech_ms,
            self._settings.vad_min_silence_ms,
        )

    async def stop(self) -> None:
        connection_ids = list(self._sessions)

        for connection_id in connection_ids:
            await self.detach_session(connection_id)

        if self.enabled:
            await self.pool.stop()

    async def attach_session(
        self,
        connection_id: str,
    ) -> bool:
        if not self.enabled:
            return False

        if connection_id in self._sessions:
            return True

        lease = self.pool.lease()

        try:
            engine = await lease.__aenter__()

        except VadCapacityError:
            vad_metrics.capacity_errors += 1

            logger.error(
                "VAD capacity exhausted connection_id=%s",
                connection_id,
            )

            return False

        detector = VadDetector(
            VadDetectorConfig(
                sample_rate=(self._settings.vad_sample_rate),
                chunk_samples=(self._settings.vad_chunk_samples),
                threshold=(self._settings.vad_threshold),
                neg_threshold=(self._settings.vad_neg_threshold),
                min_speech_ms=(self._settings.vad_min_speech_ms),
                min_silence_ms=(self._settings.vad_min_silence_ms),
                max_speech_seconds=(self._settings.vad_max_speech_seconds),
            )
        )

        session = VadSession(
            connection_id=connection_id,
            engine=engine,
            chunker=Pcm16Chunker(self._settings.vad_chunk_samples),
            detector=detector,
        )

        self._sessions[connection_id] = session

        self._leases[connection_id] = lease

        vad_metrics.sessions_total += 1
        vad_metrics.active_sessions += 1

        logger.info(
            "VAD session attached connection_id=%s",
            connection_id,
        )

        return True

    async def detach_session(
        self,
        connection_id: str,
    ) -> None:
        session = self._sessions.pop(
            connection_id,
            None,
        )

        lease = self._leases.pop(
            connection_id,
            None,
        )

        if session is None:
            return

        session.reset()

        vad_metrics.active_sessions = max(
            0,
            vad_metrics.active_sessions - 1,
        )

        if lease is not None:
            await lease.__aexit__(
                None,
                None,
                None,
            )

        logger.info(
            ("VAD session detached connection_id=%s chunks=%s"),
            connection_id,
            session.processed_chunks,
        )

    async def process_pcm(
        self,
        *,
        connection_id: str,
        session_uuid: str | None,
        payload: bytes,
    ) -> None:
        if not self.enabled:
            return

        session = self._sessions.get(connection_id)

        if session is None:
            return

        session.session_uuid = session_uuid

        try:
            events, inference_times = session.process_pcm(payload)

        except Exception:
            vad_metrics.processing_errors += 1

            logger.exception(
                ("VAD processing failure connection_id=%s uuid=%s"),
                connection_id,
                session_uuid,
            )

            return

        for inference_ms in inference_times:
            vad_metrics.chunks_processed += 1
            vad_metrics.record_inference(inference_ms)

        for event in events:
            if event.event_type == VadEventType.SPEECH_START:
                vad_metrics.speech_starts += 1

            elif event.event_type == VadEventType.SPEECH_END:
                vad_metrics.speech_ends += 1

            elif event.event_type == VadEventType.MAX_SPEECH_REACHED:
                vad_metrics.max_speech_events += 1

            logger.info(
                (
                    "VAD event=%s "
                    "connection_id=%s "
                    "uuid=%s "
                    "probability=%.3f "
                    "sample=%s "
                    "detection_delay_ms=%.1f"
                ),
                event.event_type.value,
                connection_id,
                session_uuid,
                event.probability,
                event.sample_index,
                event.detection_delay_ms,
            )


vad_service = VadService()
