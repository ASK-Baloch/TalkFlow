from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from app.realtime.llm.types import (
    LLMFallbackContext,
)

from .generation import (
    GenerationSnapshot,
    ResponseGeneration,
)

logger = logging.getLogger("talkflow.response_stream")


@dataclass(slots=True)
class StreamingResponseSession:
    connection_id: str

    generation: ResponseGeneration

    active_task: asyncio.Task | None = None


class StreamingResponseOrchestrator:
    def __init__(
        self,
        *,
        llm_service,
        response_planner,
        tts_service,
        speech_processor=None,
        assembler_factory,
    ) -> None:
        self._llm_service = llm_service

        self._response_planner = response_planner

        self._tts_service = tts_service

        self._speech_processor = speech_processor

        self._assembler_factory = assembler_factory

        self._sessions: dict[
            str,
            StreamingResponseSession,
        ] = {}

        self._lock = asyncio.Lock()

    async def attach(
        self,
        connection_id: str,
    ) -> None:
        async with self._lock:
            self._sessions.setdefault(
                connection_id,
                StreamingResponseSession(
                    connection_id=(connection_id),
                    generation=(ResponseGeneration()),
                ),
            )

    async def detach(
        self,
        connection_id: str,
    ) -> None:
        async with self._lock:
            session = self._sessions.pop(
                connection_id,
                None,
            )

        if (
            session is not None
            and session.active_task is not None
            and not session.active_task.done()
        ):
            session.active_task.cancel()

            await asyncio.gather(
                session.active_task,
                return_exceptions=True,
            )

    async def interrupt(
        self,
        connection_id: str,
    ) -> bool:
        async with self._lock:
            session = self._sessions.get(connection_id)

        if session is None:
            return False

        await session.generation.advance()

        task = session.active_task

        if task is not None and not task.done():
            task.cancel()

            return True

        return False

    async def generate_dynamic(
        self,
        *,
        context: LLMFallbackContext,
        session_uuid: str | None,
    ) -> None:
        await self.attach(context.connection_id)

        async with self._lock:
            session = self._sessions[context.connection_id]

        generation = await session.generation.current()

        current_task = asyncio.current_task()

        session.active_task = current_task

        assembler = self._assembler_factory()

        from time import perf_counter

        from app.realtime.response.metrics import response_metrics

        start_time = perf_counter()
        first_token_time = None
        first_speakable_time = None

        try:
            async for chunk in self._llm_service.stream_fallback(context):
                if first_token_time is None:
                    first_token_time = perf_counter()

                if not (await session.generation.is_current(generation)):
                    response_metrics.response_generation_invalidations_total += 1
                    return

                if chunk.text:
                    segments = assembler.push(chunk.text)

                    for segment in segments:
                        if first_speakable_time is None:
                            first_speakable_time = perf_counter()
                            response_metrics.llm_first_speakable_segment_ms.append(
                                (first_speakable_time - start_time) * 1000.0
                            )

                        await self._enqueue_segment(
                            connection_id=(context.connection_id),
                            session_uuid=(session_uuid),
                            generation=(generation),
                            session=session,
                            text=segment,
                            speech_end_ms=context.speech_end_ms,
                            expected_field=getattr(context, "expected_field", None),
                        )

                if chunk.is_final:
                    break

            for segment in assembler.flush():
                if first_speakable_time is None:
                    first_speakable_time = perf_counter()
                    response_metrics.llm_first_speakable_segment_ms.append(
                        (first_speakable_time - start_time) * 1000.0
                    )

                await self._enqueue_segment(
                    connection_id=(context.connection_id),
                    session_uuid=(session_uuid),
                    generation=(generation),
                    session=session,
                    text=segment,
                    speech_end_ms=context.speech_end_ms,
                    expected_field=getattr(context, "expected_field", None),
                )

        except asyncio.CancelledError:
            response_metrics.llm_cancellations_total += 1
            logger.info(
                "Streaming response cancelled connection_id=%s cancel_ms=%.1f",
                context.connection_id,
                (perf_counter() - start_time) * 1000.0,
            )
            raise

        finally:
            if session.active_task is current_task:
                session.active_task = None

    async def _enqueue_segment(
        self,
        *,
        connection_id: str,
        session_uuid: str | None,
        generation: GenerationSnapshot,
        session: (StreamingResponseSession),
        text: str,
        speech_end_ms: float = 0.0,
        expected_field: str | None = None,
    ) -> None:
        from app.realtime.response.metrics import response_metrics

        if not (await session.generation.is_current(generation)):
            response_metrics.stream_segments_dropped_stale_total += 1
            return

        text = text.strip()

        if not text:
            return

        response_metrics.stream_segments_total += 1

        planned = self._response_planner.plan_dynamic(text)

        if self._speech_processor:
            planned = self._speech_processor.process(
                planned,
                expected_field=expected_field,
            )

        success = await self._tts_service.enqueue(
            connection_id=(connection_id),
            planned=planned,
            session_uuid=(session_uuid),
            speech_end_ms=speech_end_ms,
        )

        if not success:
            logger.warning(
                "TTS queue full, cancelling generation connection_id=%s",
                connection_id,
            )
            raise asyncio.CancelledError("TTS queue full")
