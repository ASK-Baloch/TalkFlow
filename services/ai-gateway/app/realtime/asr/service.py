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
        
        self.is_ready = False

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

        import os

        import soundfile as sf
        
        warmup_path = "/app/scripts/test_set/001.wav"
        if os.path.exists(warmup_path):
            audio_data, _ = sf.read(warmup_path)
            warmup_audio = audio_data.astype(np.float32)
        else:
            logger.warning("Warmup fixture not found, using silence")
            warmup_audio = np.zeros(16000, dtype=np.float32)

        # We will do 3 passes to ensure complete CUDA/JIT warmup
        for i in range(1, 4):
            t0 = perf_counter_ns()
            await asyncio.to_thread(
                self.provider.transcribe,
                warmup_audio,
                beam_size=self.settings.asr_final_beam_size,
            )
            t1 = perf_counter_ns()
            logger.info("ASR warmup pass %d completed in %.1fms", i, (t1 - t0) / 1_000_000)

        logger.info("ASR ready=true")
        self.is_ready = True

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

        if not session.active_utterance_id:
            return
            
        active = session.get_utterance(session.active_utterance_id)
        if not active:
            return

        if active.partial_inflight or active.tentative_inflight or active.finalized:
            return

        audio = session.utterance.snapshot()

        audio_ms = audio.size / session.sample_rate * 1000

        if audio_ms < self.settings.asr_partial_min_audio_ms:
            return

        if (
            audio_ms - active.last_partial_audio_ms
            < self.settings.asr_partial_interval_ms
        ):
            return

        active.revision += 1
        active.partial_inflight = True
        active.last_partial_audio_ms = audio_ms

        await self.scheduler.submit(
            AsrJob(
                priority=10,
                sequence=next(self.scheduler._sequence),
                connection_id=session.connection_id,
                session_uuid=session.session_uuid,
                utterance_id=active.utterance_id,
                transcript_type=TranscriptType.PARTIAL,
                revision=active.revision,
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
            logger.info("VAD speech_start sample=%s", event.sample_index)

        elif event.event_type == VadEventType.SPEECH_PENDING_END:
            logger.info(
                "VAD pending_end sample=%s",
                event.sample_index
            )
            
            if session.active_utterance_id:
                active = session.get_utterance(session.active_utterance_id)
                if active:
                    audio = session.utterance.snapshot()
                    
                    # Trim the same way as final
                    trailing_trim_ms = max(0, event.detection_delay_ms - 100)
                    leading_trim_ms = max(0, self.settings.asr_pre_roll_ms - 100)
                    
                    sample_rate = self.settings.asr_sample_rate
                    
                    start_idx = int(leading_trim_ms * sample_rate / 1000)
                    end_trim_idx = int(trailing_trim_ms * sample_rate / 1000)
                    
                    if end_trim_idx > 0:
                        audio = audio[start_idx:-end_trim_idx]
                    else:
                        audio = audio[start_idx:]
                        
                    active.revision += 1
                    active.tentative_inflight = True
                    active.acoustic_end_ns = perf_counter_ns() - int(event.detection_delay_ms * 1_000_000)
                    
                    await self.scheduler.submit(
                        AsrJob(
                            priority=1,
                            sequence=next(self.scheduler._sequence),
                            connection_id=session.connection_id,
                            session_uuid=session.session_uuid,
                            utterance_id=active.utterance_id,
                            transcript_type=TranscriptType.FINAL_TENTATIVE,
                            revision=active.revision,
                            audio=audio.copy(),
                            beam_size=self.settings.asr_final_beam_size,
                            stream=session.asr_stream,
                            acoustic_end_ns=active.acoustic_end_ns,
                        )
                    )

        elif event.event_type == VadEventType.SPEECH_RESUMED:
            logger.info(
                "VAD speech_resumed silence_ms=%.1f\nVAD pending_end_cancelled\nsame_utterance=true",
                event.detection_delay_ms
            )
            if session.active_utterance_id:
                active = session.get_utterance(session.active_utterance_id)
                if active:
                    active.tentative_result = None
                    active.revision += 1

        elif (
            event.event_type == VadEventType.SPEECH_END
            or event.event_type == VadEventType.MAX_SPEECH_REACHED
        ):
            session.finish_utterance()
            
            logger.info(
                "VAD %s sample=%s silence_ms=%.1f",
                event.event_type.value,
                event.sample_index,
                event.detection_delay_ms
            )

            if not session.active_utterance_id:
                return

            active = session.get_utterance(session.active_utterance_id)
            if not active:
                return

            audio = session.utterance.snapshot()
            
            sample_rate = self.settings.asr_sample_rate
            original_duration_ms = len(audio) / sample_rate * 1000

            trailing_trim_ms = max(0, event.detection_delay_ms - 100)
            leading_trim_ms = max(0, self.settings.asr_pre_roll_ms - 100)
            
            start_idx = int(leading_trim_ms * sample_rate / 1000)
            end_trim_idx = int(trailing_trim_ms * sample_rate / 1000)
            
            # Save first 5 validation cases
            if not hasattr(self, '_trim_validation_count'):
                self._trim_validation_count = 0
            if self._trim_validation_count < 5:
                import os

                import soundfile as sf
                os.makedirs("/app/test_set/trim_validation", exist_ok=True)
                try:
                    sf.write(f"/app/test_set/trim_validation/untrimmed_{self._trim_validation_count}.wav", audio, sample_rate)
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to save debug untrimmed file: {e}")
            
            if end_trim_idx > 0:
                trimmed_audio = audio[start_idx:-end_trim_idx]
            else:
                trimmed_audio = audio[start_idx:]
                
            if self._trim_validation_count < 5:
                try:
                    sf.write(f"/app/test_set/trim_validation/trimmed_{self._trim_validation_count}.wav", trimmed_audio, sample_rate)
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to save debug trimmed file: {e}")
                self._trim_validation_count += 1
                
            trimmed_duration_ms = len(trimmed_audio) / sample_rate * 1000
            logger.info(
                "VAD audio trim: original=%.1fms trailing_trim=%.1fms leading_trim=%.1fms trimmed=%.1fms",
                original_duration_ms, trailing_trim_ms, leading_trim_ms, trimmed_duration_ms
            )

            active.finalized = True
            
            # Only bump revision if no FINAL_TENTATIVE is in flight.
            if not active.tentative_inflight:
                active.revision += 1

            if active.tentative_result:
                # Speculative decode already finished — promote it to FINAL.
                logger.info("VAD speech_end utilizing FINAL_TENTATIVE result (pre-arrived)")
                tentative = active.tentative_result
                tentative.transcript_type = TranscriptType.FINAL
                tentative.revision = active.revision
                await self.handle_transcript(tentative)
                return

            if active.tentative_inflight:
                # FINAL_TENTATIVE still running — let it arrive and promote itself.
                logger.info("VAD speech_end waiting for in-flight FINAL_TENTATIVE (revision=%s)", active.revision)
                return

            if not active.acoustic_end_ns:
                active.acoustic_end_ns = perf_counter_ns() - int(event.detection_delay_ms * 1_000_000)

            await self.scheduler.submit(
                AsrJob(
                    priority=0,
                    sequence=next(self.scheduler._sequence),
                    connection_id=session.connection_id,
                    session_uuid=session.session_uuid,
                    utterance_id=active.utterance_id,
                    transcript_type=TranscriptType.FINAL,
                    revision=active.revision,
                    audio=trimmed_audio.copy(),
                    beam_size=self.settings.asr_final_beam_size,
                    stream=session.asr_stream,
                    acoustic_end_ns=active.acoustic_end_ns,
                )
            )

    async def handle_transcript(self, event: TranscriptEvent):
        if not self.enabled:
            return

        session = self.sessions.get(event.connection_id)
        if session is None:
            return

        utterance = session.get_utterance(event.utterance_id)
        if utterance is None:
            logger.info("ASR event discarded (unknown utterance)")
            return

        rtf = 0.0
        if event.audio_duration_ms > 0:
            rtf = event.decode_ms / event.audio_duration_ms

        if event.transcript_type == TranscriptType.PARTIAL:
            utterance.partial_inflight = False

            if utterance.finalized or utterance.cancelled or event.revision != utterance.revision or utterance.final_emitted:
                asr_metrics.stale_partials_dropped += 1
                return

            asr_metrics.partials_emitted += 1
            asr_metrics.partial_decode_ms.append(event.decode_ms)

            first_partial_latency_ms = None
            if event.text and not utterance.first_partial_emitted:
                utterance.first_partial_emitted = True
                if utterance.speech_start_ns:
                    first_partial_latency_ms = (
                        perf_counter_ns() - utterance.speech_start_ns
                    ) / 1_000_000.0
                    asr_metrics.first_partial_latency_ms.append(first_partial_latency_ms)

            # Audio available -> partial result is queue + decode
            processing_latency_ms = event.queue_wait_ms + event.decode_ms

            log_msg = (
                f"ASR PARTIAL "
                f"uuid={event.session_uuid} "
                f"utterance={event.utterance_id} "
                f"revision={event.revision} "
                f"text='{event.text}' "
                f"decode_ms={event.decode_ms:.1f} "
                f"queue_ms={event.queue_wait_ms:.1f} "
                f"processing_latency_ms={processing_latency_ms:.1f} "
                f"rtf={rtf:.3f}"
            )
            if first_partial_latency_ms is not None:
                log_msg += f" first_partial_latency_ms={first_partial_latency_ms:.1f}"

            logger.info(log_msg)

        elif event.transcript_type == TranscriptType.FINAL_TENTATIVE:
            utterance.tentative_inflight = False
            
            if utterance.cancelled or event.revision != utterance.revision or utterance.final_emitted:
                logger.info("ASR FINAL_TENTATIVE discarded (stale) text='%s'", event.text)
                return
                
            acoustic_delay = (event.job_created_ns - event.acoustic_end_ns) / 1_000_000.0 if event.acoustic_end_ns else 0
            tentative_queue = (event.decode_start_ns - event.job_created_ns) / 1_000_000.0
            model_compute = (event.decode_done_ns - event.decode_start_ns) / 1_000_000.0
            
            if utterance.finalized:
                # SPEECH_END already fired and waited for us — promote directly to FINAL
                logger.info(
                    "ASR FINAL_TENTATIVE->FINAL (speculative hit) text='%s' decode_ms=%.1f acoustic_delay=%.1f queue=%.1f compute=%.1f",
                    event.text, event.decode_ms, acoustic_delay, tentative_queue, model_compute
                )
                event.transcript_type = TranscriptType.FINAL
                await self.handle_transcript(event)
                return
                
            logger.info(
                "ASR FINAL_TENTATIVE text='%s' decode_ms=%.1f acoustic_delay=%.1f queue=%.1f compute=%.1f",
                event.text, event.decode_ms, acoustic_delay, tentative_queue, model_compute
            )
            
            # Store it; SPEECH_END will promote it when it fires
            utterance.tentative_result = event

        elif event.transcript_type == TranscriptType.FINAL:
            if utterance.final_emitted:
                logger.info("ASR FINAL discarded (duplicate) text='%s'", event.text)
                return
            utterance.final_emitted = True

            final_after_speech_end_ms = 0.0
            
            utterance.finalized = True
            if utterance.speech_end_ns:
                final_after_speech_end_ms = (
                    perf_counter_ns() - utterance.speech_end_ns
                ) / 1_000_000.0
                    
            endpointing_ms = (utterance.speech_end_ns - utterance.speech_start_ns) / 1_000_000.0 if utterance.speech_end_ns and utterance.speech_start_ns else 0
            final_queue_ms = (event.worker_start_ns - event.job_created_ns) / 1_000_000.0 if event.worker_start_ns > 0 else event.queue_wait_ms
            final_decode_ms = (event.decode_done_ns - event.decode_start_ns) / 1_000_000.0 if event.decode_done_ns > 0 else event.decode_ms
            final_emit_overhead_ms = (event.emit_ns - event.decode_done_ns) / 1_000_000.0 if event.emit_ns > 0 else 0
            
            T0 = event.acoustic_end_ns
            T4 = utterance.speech_end_ns if utterance else 0
            T5 = event.emit_ns if event.emit_ns > 0 else perf_counter_ns()
            
            acoustic_end_to_final_ms = (T5 - T0) / 1_000_000.0 if T0 else 0
            committed_end_to_final_ms = (T5 - T4) / 1_000_000.0 if T4 else 0
            
            logger.info(
                (
                    "ASR FINAL "
                    "uuid=%s "
                    "utterance=%s "
                    "text='%s' "
                    "endpointing_ms=%.1f "
                    "final_queue_ms=%.1f "
                    "final_decode_ms=%.1f "
                    "final_emit_overhead_ms=%.1f "
                    "speech_end_to_final_ms=%.1f "
                    "acoustic_end_to_final_ms=%.1f "
                    "committed_end_to_final_ms=%.1f "
                    "rtf=%.3f"
                ),
                event.session_uuid,
                event.utterance_id,
                event.text,
                endpointing_ms,
                final_queue_ms,
                final_decode_ms,
                final_emit_overhead_ms,
                final_after_speech_end_ms,
                acoustic_end_to_final_ms,
                committed_end_to_final_ms,
                rtf,
            )


asr_service = AsrService()
