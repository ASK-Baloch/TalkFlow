from __future__ import annotations

import asyncio
import logging
from time import (
    perf_counter,
    perf_counter_ns,
)

from app.realtime.providers.tts import (
    TTSProvider,
    TTSRequest,
)

from .interruption import (
    PlaybackGeneration,
)
from .metrics import (
    tts_metrics,
)
from .planner import (
    PlannedResponse,
    TTSRoute,
)
from .playback import (
    AudioSocketPcmPlayer,
    PlaybackInterrupted,
)
from .session import (
    TtsCallSession,
)
from .types import (
    PlaybackRequest,
    ResponseId,
)

logger = logging.getLogger("talkflow.tts")


class TTSService:
    def __init__(
        self,
        *,
        enabled: bool = True,
        pregenerated_provider: TTSProvider,
        dynamic_provider: TTSProvider,
        sample_rate: int,
        sample_width_bytes: int,
        frame_ms: int,
        queue_size: int,
        interrupt_enabled: bool,
        flush_queue_on_interrupt: bool,
        drop_stale_audio: bool,
        barge_in_log_events: bool,
    ) -> None:
        self.pregenerated_provider = pregenerated_provider

        self.dynamic_provider = dynamic_provider

        self.queue_size = queue_size

        self.interrupt_enabled = interrupt_enabled

        self.flush_queue_on_interrupt = flush_queue_on_interrupt

        self.drop_stale_audio = drop_stale_audio

        self.barge_in_log_events = barge_in_log_events

        self.enabled = enabled

        self.player = AudioSocketPcmPlayer(
            sample_rate=sample_rate,
            sample_width_bytes=(sample_width_bytes),
            frame_ms=frame_ms,
        )

        self._sessions: dict[
            str,
            TtsCallSession,
        ] = {}

    @property
    def connected_calls(self) -> int:
        return len(self._sessions)

    async def start(
        self,
    ) -> None:
        await self.pregenerated_provider.start()

        await self.dynamic_provider.start()

    async def stop(
        self,
    ) -> None:
        for connection_id in list(self._sessions):
            await self.detach_connection(connection_id)

        await self.dynamic_provider.stop()

        await self.pregenerated_provider.stop()

    async def attach_connection(
        self,
        *,
        connection_id: str,
        writer: asyncio.StreamWriter,
    ) -> None:
        if connection_id in self._sessions:
            return

        queue: asyncio.Queue[PlaybackRequest] = asyncio.Queue(maxsize=self.queue_size)

        session = TtsCallSession(
            connection_id=(connection_id),
            writer=writer,
            queue=queue,
            generation=(PlaybackGeneration(connection_id=(connection_id))),
        )

        session.worker_task = asyncio.create_task(self._playback_worker(session))

        self._sessions[connection_id] = session

        tts_metrics.playback_sessions_total += 1

        logger.info(
            "TTS session attached connection_id=%s",
            connection_id,
        )

    async def detach_connection(
        self,
        connection_id: str,
    ) -> None:
        session = self._sessions.pop(
            connection_id,
            None,
        )

        if session is None:
            return

        await self._cancel_current_playback(session)

        if session.worker_task:
            session.worker_task.cancel()

            await asyncio.gather(
                session.worker_task,
                return_exceptions=True,
            )

        self._flush_queue(session)

        logger.info(
            "TTS session detached connection_id=%s",
            connection_id,
        )

    async def enqueue(
        self,
        *,
        connection_id: str,
        planned: PlannedResponse,
        session_uuid: str | None = None,
        speech_end_ms: float = 0.0,
    ) -> bool:
        session = self._sessions.get(connection_id)

        if session is None:
            logger.warning(
                "TTS session missing connection_id=%s",
                connection_id,
            )

            return False

        generation = await session.generation.current()

        if planned.route == TTSRoute.PREGENERATED:
            if not planned.response_id:
                raise ValueError("Pregenerated response requires response_id")

            request = PlaybackRequest(
                connection_id=(connection_id),
                generation=generation,
                response_id=(ResponseId(planned.response_id)),
                session_uuid=(session_uuid),
                speech_end_ms=speech_end_ms,
            )

        else:
            text = planned.tts_text or planned.display_text
            if not text:
                raise ValueError("Dynamic response requires text")

            request = PlaybackRequest(
                connection_id=(connection_id),
                generation=generation,
                text=text,
                session_uuid=(session_uuid),
                speech_end_ms=speech_end_ms,
            )

        if session.queue.full():
            tts_metrics.queue_overflows += 1

            logger.error(
                "TTS queue full connection_id=%s",
                connection_id,
            )

            return False

        session.queue.put_nowait(request)

        tts_metrics.requests_total += 1

        return True

    async def interrupt(
        self,
        *,
        connection_id: str,
        reason: str = "caller_speech",
    ) -> bool:
        if not self.interrupt_enabled:
            return False

        session = self._sessions.get(connection_id)

        if session is None:
            return False

        interrupt_started = perf_counter()

        new_generation = await session.generation.advance()

        tts_metrics.interruptions_total += 1

        if self.barge_in_log_events:
            logger.info(
                "TTS interruption connection_id=%s reason=%s generation=%s",
                connection_id,
                reason,
                new_generation,
            )

        cancelled = await self._cancel_current_playback(session)

        if self.flush_queue_on_interrupt:
            flushed = self._flush_queue(session)

            tts_metrics.flushed_requests_total += flushed

        elapsed_ms = (perf_counter() - interrupt_started) * 1000.0

        tts_metrics.barge_in_cancel_ms.append(elapsed_ms)

        return cancelled

    async def is_playing(
        self,
        connection_id: str,
    ) -> bool:
        session = self._sessions.get(connection_id)

        if session is None:
            return False

        task = session.current_playback_task

        return task is not None and not task.done()

    async def playback_age_ms(
        self,
        connection_id: str,
    ) -> float | None:
        session = self._sessions.get(connection_id)

        if session is None or session.playback_started_at is None:
            return None

        return (perf_counter() - session.playback_started_at) * 1000.0

    def _provider_for_request(
        self,
        request: PlaybackRequest,
    ) -> TTSProvider:
        return (
            self.pregenerated_provider if request.response_id else self.dynamic_provider
        )

    async def _cancel_current_playback(
        self,
        session: TtsCallSession,
    ) -> bool:
        task = session.current_playback_task

        if task is None or task.done():
            return False

        request = session.current_request

        if request is not None:
            provider = self._provider_for_request(request)

            if provider is not None and provider.supports_cancellation:
                try:
                    await provider.cancel(request.request_id)

                except Exception:
                    logger.exception(
                        "TTS provider cancellation failed connection_id=%s request_id=%s",
                        session.connection_id,
                        request.request_id,
                    )

        task.cancel()

        await asyncio.gather(
            task,
            return_exceptions=True,
        )

        session.current_playback_task = None

        tts_metrics.interrupted_playbacks_total += 1

        return True

    def _flush_queue(
        self,
        session: TtsCallSession,
    ) -> int:
        count = 0

        while True:
            try:
                request = session.queue.get_nowait()

            except asyncio.QueueEmpty:
                break

            else:
                del request
                session.queue.task_done()
                count += 1

        return count

    async def _playback_worker(
        self,
        session: TtsCallSession,
    ) -> None:
        while True:
            request = await session.queue.get()

            try:
                current_generation = await session.generation.current()

                if self.drop_stale_audio and request.generation != current_generation:
                    tts_metrics.stale_requests_dropped_total += 1

                    continue

                session.current_request = request

                task = asyncio.create_task(
                    self._play_request(
                        session=session,
                        request=request,
                    )
                )

                session.current_playback_task = task

                await task

            except asyncio.CancelledError:
                pass

            except PlaybackInterrupted:
                pass

            except Exception:
                tts_metrics.playback_errors += 1

                logger.exception(
                    "TTS playback failed connection_id=%s",
                    session.connection_id,
                )

            finally:
                session.current_playback_task = None

                session.current_request = None

                session.queue.task_done()

    async def _play_request(
        self,
        *,
        session: TtsCallSession,
        request: PlaybackRequest,
    ) -> None:
        if request.response_id:
            provider = self.pregenerated_provider

            provider_request = TTSRequest(
                response_id=(request.response_id.value),
                request_id=(request.request_id),
            )

        else:
            provider = self.dynamic_provider

            provider_request = TTSRequest(
                text=request.text,
                request_id=(request.request_id),
            )

        async def should_continue():
            if not self.drop_stale_audio:
                return True

            return await session.generation.is_current(request.generation)

        first_audio_sent = False

        async def on_first_frame():
            nonlocal first_audio_sent

            if first_audio_sent:
                return

            first_audio_sent = True

            elapsed_ms = (perf_counter_ns() - request.created_ns) / 1_000_000.0

            tts_metrics.first_audio_ms.append(elapsed_ms)

            if request.speech_end_ms > 0:
                from app.realtime.response.metrics import response_metrics

                response_metrics.speech_end_to_first_bot_audio_ms.append(
                    (perf_counter() * 1000.0) - request.speech_end_ms
                )

        chunks = provider.stream(provider_request)

        tts_metrics.active_playbacks += 1

        session.playback_started_at = perf_counter()

        try:
            await self.player.play_chunks(
                writer=session.writer,
                chunks=chunks,
                should_continue=(should_continue),
                on_first_frame=(on_first_frame),
            )

            if not await should_continue():
                raise PlaybackInterrupted

            tts_metrics.completed_total += 1

        finally:
            tts_metrics.active_playbacks = max(
                0,
                tts_metrics.active_playbacks - 1,
            )

            session.playback_started_at = None
