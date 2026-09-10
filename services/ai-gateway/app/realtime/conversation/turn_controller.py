from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

logger = logging.getLogger("talkflow.turn_controller")


class LLMCancellationService(Protocol):
    async def cancel(
        self,
        connection_id: str,
    ) -> bool: ...


class TTSCancellationService(Protocol):
    async def interrupt(
        self,
        connection_id: str,
    ) -> bool: ...


class ResponseCancellationService(Protocol):
    async def interrupt(
        self,
        connection_id: str,
    ) -> bool: ...


@dataclass(slots=True)
class TurnInterruptionResult:
    connection_id: str

    llm_cancelled: bool
    tts_interrupted: bool
    response_interrupted: bool

    latency_ms: float


class ConversationTurnController:
    """
    Conversation-level orchestration.

    This class is intentionally the ONLY layer
    that coordinates cancellation across LLM
    generation and TTS playback.

    LLMService and TTSService remain unaware of
    one another.
    """

    def __init__(
        self,
        *,
        llm_service: (LLMCancellationService | None),
        tts_service: (TTSCancellationService | None),
        response_orchestrator: (ResponseCancellationService | None) = None,
    ) -> None:
        self._llm_service = llm_service

        self._tts_service = tts_service

        self._response_orchestrator = response_orchestrator

    async def interrupt_turn(
        self,
        *,
        connection_id: str,
    ) -> TurnInterruptionResult:
        started = perf_counter()

        llm_cancelled = False
        tts_interrupted = False
        response_interrupted = False

        tasks: list[asyncio.Task] = []

        if self._llm_service is not None:
            tasks.append(
                asyncio.create_task(
                    self._llm_service.cancel(connection_id=connection_id),
                    name=(f"cancel-llm-{connection_id}"),
                )
            )

        if self._tts_service is not None:
            tasks.append(
                asyncio.create_task(
                    self._tts_service.interrupt(connection_id=connection_id),
                    name=(f"interrupt-tts-{connection_id}"),
                )
            )

        if self._response_orchestrator is not None:
            tasks.append(
                asyncio.create_task(
                    self._response_orchestrator.interrupt(connection_id=connection_id),
                    name=(f"interrupt-response-{connection_id}"),
                )
            )

        results = []

        if tasks:
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

        index = 0

        if self._llm_service is not None:
            result = results[index]
            index += 1

            if isinstance(
                result,
                BaseException,
            ):
                logger.warning(
                    "LLM cancellation failed connection_id=%s: %r",
                    connection_id,
                    result,
                )
            else:
                llm_cancelled = bool(result)

        if self._tts_service is not None:
            result = results[index]
            index += 1

            if isinstance(
                result,
                BaseException,
            ):
                logger.warning(
                    "TTS interruption failed connection_id=%s: %r",
                    connection_id,
                    result,
                )
            else:
                tts_interrupted = bool(result)

        if self._response_orchestrator is not None:
            result = results[index]
            index += 1

            if isinstance(
                result,
                BaseException,
            ):
                logger.warning(
                    "Response interruption failed connection_id=%s: %r",
                    connection_id,
                    result,
                )
            else:
                response_interrupted = bool(result)

        latency_ms = (perf_counter() - started) * 1000.0

        logger.info(
            "Conversation turn interrupted "
            "connection_id=%s "
            "llm_cancelled=%s "
            "tts_interrupted=%s "
            "response_interrupted=%s "
            "latency_ms=%.2f",
            connection_id,
            llm_cancelled,
            tts_interrupted,
            response_interrupted,
            latency_ms,
        )

        return TurnInterruptionResult(
            connection_id=connection_id,
            llm_cancelled=(llm_cancelled),
            tts_interrupted=(tts_interrupted),
            response_interrupted=(response_interrupted),
            latency_ms=latency_ms,
        )
