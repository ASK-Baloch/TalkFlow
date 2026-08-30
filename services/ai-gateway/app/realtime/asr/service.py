import asyncio
import logging
from time import perf_counter_ns

import numpy as np

logger = logging.getLogger("talkflow.asr")

from app.core.config import get_settings
from app.realtime.vad.types import VadEvent, VadEventType

from .metrics import asr_metrics
from .scheduler import AsrJob, AsrScheduler
from .types import TranscriptEvent, TranscriptType


class AsrService:
    def __init__(self):
        settings = get_settings()

        self.enabled = settings.asr_enabled

        self.settings = settings

        self.sessions = {}

        self.provider = None
        self.scheduler = None

    async def start(self):
        if not self.enabled:
            return

        if self.settings.asr_provider == "nemo":
            from .nemo_provider import NemoProvider
            self.provider = await asyncio.to_thread(
                NemoProvider,
                model_path=self.settings.asr_model,
                device=self.settings.asr_device,
            )
        else:
            from .faster_whisper import FasterWhisperProvider
            self.provider = await asyncio.to_thread(
                FasterWhisperProvider,
                model_name=self.settings.asr_model,
                device=self.settings.asr_device,
                compute_type=(self.settings.asr_compute_type),
                language=(self.settings.asr_language),
                condition_on_previous_text=(self.settings.asr_condition_on_previous_text),
                word_timestamps=(self.settings.asr_word_timestamps),
                initial_prompt=(self.settings.asr_initial_prompt),
            )

        self.scheduler = AsrScheduler(
            provider=self.provider,
            maxsize=(self.settings.asr_queue_maxsize),
            workers=(self.settings.asr_workers),
        )

        self.scheduler.result_handler = self.handle_transcript

        await self.scheduler.start()

        warmup_audio = np.zeros(
            16000,
            dtype=np.float32,
        )

        await asyncio.to_thread(
            self.provider.transcribe,
            warmup_audio,
            beam_size=1,
        )

        logger.info("ASR warmup completed")

    async def attach_session(self, connection_id: str) -> None:
        if not self.enabled:
            return

        from .session import AsrSession

        self.sessions[connection_id] = AsrSession(
            connection_id=connection_id,
            input_sample_rate=self.settings.asr_input_sample_rate,
            sample_rate=self.settings.asr_sample_rate,
            pre_roll_ms=self.settings.asr_pre_roll_ms,
        )

    async def detach_session(self, connection_id: str) -> None:
        self.sessions.pop(connection_id, None)

    async def push_pcm(
        self, connection_id: str, session_uuid: str | None, payload: bytes
    ):
        if not self.enabled:
            return

        session = self.sessions.get(connection_id)
        if session is None:
            return
            
        session.session_uuid = session_uuid
        session.process_pcm(payload)
        
        await self.maybe_schedule_partial(session)

    async def maybe_schedule_partial(self, session):
        if not self.settings.asr_partial_enabled:
            return

        if not session.speaking:
            return

        if session.partial_inflight:
            return

        audio = session.utterance.snapshot()

        audio_ms = audio.size / session.sample_rate * 1000

        if audio_ms < self.settings.asr_partial_min_audio_ms:
            return

        if (
            audio_ms - session.last_partial_audio_ms
            < self.settings.asr_partial_interval_ms
        ):
            return

        session.revision += 1
        session.partial_inflight = True
        session.last_partial_audio_ms = audio_ms

        await self.scheduler.submit(
            AsrJob(
                priority=10,
                sequence=next(self.scheduler._sequence),
                connection_id=session.connection_id,
                session_uuid=session.session_uuid,
                utterance_id=session.utterance_id,
                transcript_type=TranscriptType.PARTIAL,
                revision=session.revision,
                audio=audio.copy(),
                beam_size=self.settings.asr_partial_beam_size,
                stream=session.asr_stream,
            )
        )

    async def handle_vad_event(
        self, connection_id: str, session_uuid: str | None, event: VadEvent
    ):
        if not self.enabled:
            return

        session = self.sessions.get(connection_id)
        if session is None:
            return

        if event.event_type == VadEventType.SPEECH_START:
            session.session_uuid = session_uuid
            
            # Open a new stateful stream for this utterance
            asr_stream = None
            if self.provider:
                from app.core.config import get_asr_vocabulary
                vocab = get_asr_vocabulary()
                
                # Combine global terms with dynamic state hints passed from the application
                active_hints = list(set(vocab.get("global", []) + session.context_hints))
                
                asr_stream = self.provider.open_stream(
                    beam_size=self.settings.asr_final_beam_size,
                    context_hints=active_hints
                )
            
            session.start_utterance(asr_stream=asr_stream)

        elif (
            event.event_type == VadEventType.SPEECH_END
            or event.event_type == VadEventType.MAX_SPEECH_REACHED
        ):
            session.finish_utterance()

            if not session.utterance_id:
                return

            audio = session.utterance.snapshot()

            session.finalized = True
            session.revision += 1

            await self.scheduler.submit(
                AsrJob(
                    priority=0,
                    sequence=next(self.scheduler._sequence),
                    connection_id=session.connection_id,
                    session_uuid=session.session_uuid,
                    utterance_id=session.utterance_id,
                    transcript_type=TranscriptType.FINAL,
                    revision=session.revision,
                    audio=audio.copy(),
                    beam_size=self.settings.asr_final_beam_size,
                    stream=session.asr_stream,
                )
            )

    async def handle_transcript(self, event: TranscriptEvent):
        if not self.enabled:
            return

        session = self.sessions.get(event.connection_id)

        rtf = 0.0
        if event.audio_duration_ms > 0:
            rtf = event.decode_ms / event.audio_duration_ms

        if event.transcript_type == TranscriptType.PARTIAL:
            if session is None:
                return
                
            session.partial_inflight = False

            if session.finalized or event.utterance_id != session.utterance_id:
                asr_metrics.stale_partials_dropped += 1
                return

            asr_metrics.partials_emitted += 1
            asr_metrics.partial_decode_ms.append(event.decode_ms)

            first_partial_latency_ms = 0.0
            if event.text and not session.first_partial_emitted:
                session.first_partial_emitted = True
                if session.speech_start_ns:
                    first_partial_latency_ms = (
                        perf_counter_ns() - session.speech_start_ns
                    ) / 1_000_000.0
                    asr_metrics.first_partial_latency_ms.append(first_partial_latency_ms)

            logger.info(
                (
                    "ASR PARTIAL "
                    "uuid=%s "
                    "utterance=%s "
                    "revision=%s "
                    "text='%s' "
                    "decode_ms=%.1f "
                    "rtf=%.3f "
                    "first_partial_latency_ms=%.1f"
                ),
                event.session_uuid,
                event.utterance_id,
                event.revision,
                event.text,
                event.decode_ms,
                rtf,
                first_partial_latency_ms,
            )

        elif event.transcript_type == TranscriptType.FINAL:
            final_after_speech_end_ms = 0.0
            
            if session is not None:
                session.finalized = True
                if session.speech_end_ns:
                    final_after_speech_end_ms = (
                        perf_counter_ns() - session.speech_end_ns
                    ) / 1_000_000.0

            asr_metrics.finals_emitted += 1
            asr_metrics.final_decode_ms.append(event.decode_ms)

            logger.info(
                (
                    "ASR FINAL "
                    "uuid=%s "
                    "utterance=%s "
                    "text='%s' "
                    "decode_ms=%.1f "
                    "rtf=%.3f "
                    "final_after_speech_end_ms=%.1f"
                ),
                event.session_uuid,
                event.utterance_id,
                event.text,
                event.decode_ms,
                rtf,
                final_after_speech_end_ms,
            )


asr_service = AsrService()
