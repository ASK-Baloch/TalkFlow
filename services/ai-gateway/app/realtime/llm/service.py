from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from uuid import uuid4

import httpx

from app.realtime.providers.llm import (
    LLMProvider,
    LLMRequest,
)

from .fallback import build_fallback_messages
from .metrics import llm_metrics
from .types import (
    LLMFallbackContext,
    LLMFallbackResult,
)

logger = logging.getLogger("talkflow.llm")


@dataclass(slots=True)
class ActiveLLMRequest:
    connection_id: str
    request_id: str
    task: asyncio.Task | None = None


class LLMService:
    def __init__(
        self,
        *,
        provider: LLMProvider,
        enabled: bool,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int | None,
        presence_penalty: float,
        enable_thinking: bool,
        max_history_turns: int,
        max_input_chars: int,
    ) -> None:
        self.provider = provider
        self.enabled = enabled

        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.presence_penalty = presence_penalty
        self.enable_thinking = enable_thinking
        self.max_history_turns = max_history_turns
        self.max_input_chars = max_input_chars

        self._active: dict[str, ActiveLLMRequest] = {}
        self._active_lock = asyncio.Lock()

    async def start(self) -> None:
        if self.enabled:
            await self.provider.start()

    async def stop(self) -> None:
        async with self._active_lock:
            active = list(self._active.values())

        for item in active:
            if item.task is not None:
                item.task.cancel()

        if active:
            await asyncio.gather(
                *[item.task for item in active if item.task is not None],
                return_exceptions=True,
            )

        async with self._active_lock:
            self._active.clear()

        if self.enabled:
            await self.provider.stop()

    async def health(self) -> dict:
        if not self.enabled:
            return {
                "enabled": False,
                "ready": True,
            }

        provider_health = await self.provider.health()

        async with self._active_lock:
            active_requests = len(self._active)

        return {
            "enabled": True,
            "active_requests": active_requests,
            "provider": provider_health,
        }

    def _build_request(self, context: LLMFallbackContext) -> LLMRequest:
        return LLMRequest(
            messages=(
                build_fallback_messages(
                    context,
                    max_history_turns=self.max_history_turns,
                    max_input_chars=self.max_input_chars,
                )
            ),
            request_id=str(uuid4()),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            presence_penalty=self.presence_penalty,
            enable_thinking=self.enable_thinking,
        )

    async def _register(
        self,
        *,
        connection_id: str,
        request_id: str,
    ) -> None:
        task = asyncio.current_task()

        async with self._active_lock:
            old = self._active.get(connection_id)

            if old is not None and old.task is not None and old.task is not task:
                old.task.cancel()

            self._active[connection_id] = ActiveLLMRequest(
                connection_id=connection_id,
                request_id=request_id,
                task=task,
            )

    async def _unregister(
        self,
        *,
        connection_id: str,
        request_id: str,
    ) -> None:
        async with self._active_lock:
            current = self._active.get(connection_id)

            if current is not None and current.request_id == request_id:
                self._active.pop(connection_id, None)

    async def cancel(self, connection_id: str) -> bool:
        """
        Cancel ONLY LLM generation.

        This method must never call the audio synthesis service.
        """
        async with self._active_lock:
            active = self._active.get(connection_id)

        if active is None:
            return False

        provider_cancelled = False

        if self.provider.supports_cancellation:
            try:
                provider_cancelled = await self.provider.cancel(active.request_id)
            except Exception:
                logger.exception(
                    "LLM provider cancel failed connection_id=%s request_id=%s",
                    connection_id,
                    active.request_id,
                )

        if (
            active.task is not None
            and not active.task.done()
            and active.task is not asyncio.current_task()
        ):
            active.task.cancel()

        return provider_cancelled or active.task is not None

    async def generate_fallback(
        self,
        context: LLMFallbackContext,
    ) -> LLMFallbackResult | None:
        if not self.enabled:
            llm_metrics.fallback_skipped_total += 1
            return None

        request = self._build_request(context)
        assert request.request_id

        await self._register(
            connection_id=context.connection_id,
            request_id=request.request_id,
        )

        llm_metrics.requests_total += 1

        try:
            result = await self.provider.generate(request)

        except (
            asyncio.TimeoutError,
            httpx.TimeoutException,
        ):
            llm_metrics.timeouts_total += 1
            logger.warning(
                "LLM request timed out connection_id=%s",
                context.connection_id,
            )
            return None

        except asyncio.CancelledError:
            logger.info(
                "LLM generation cancelled connection_id=%s request_id=%s",
                context.connection_id,
                request.request_id,
            )
            raise

        except Exception:
            llm_metrics.failures_total += 1
            logger.exception(
                "LLM request failed connection_id=%s",
                context.connection_id,
            )
            return None

        finally:
            await self._unregister(
                connection_id=context.connection_id,
                request_id=request.request_id,
            )

        text = result.text.strip()
        if not text:
            llm_metrics.empty_responses_total += 1
            return None

        llm_metrics.completed_total += 1
        if result.latency_ms is not None:
            llm_metrics.latency_ms.append(result.latency_ms)

        logger.info(
            "LLM request completed connection_id=%s request_id=%s provider=%s model=%s latency_ms=%.1f prompt_tokens=%s completion_tokens=%s fallback_used=%s",
            context.connection_id,
            request.request_id,
            self.provider.provider_name,
            result.model,
            result.latency_ms or 0.0,
            result.prompt_tokens,
            result.completion_tokens,
            True,
        )

        return LLMFallbackResult(
            text=text,
            latency_ms=(result.latency_ms or 0.0),
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
        )

    async def stream_fallback(
        self,
        context: LLMFallbackContext,
    ):
        if not self.enabled:
            llm_metrics.fallback_skipped_total += 1
            return

        request = self._build_request(context)
        assert request.request_id

        await self._register(
            connection_id=context.connection_id,
            request_id=request.request_id,
        )

        llm_metrics.requests_total += 1

        try:
            async for chunk in self.provider.stream(request):
                yield chunk

        except (
            asyncio.TimeoutError,
            httpx.TimeoutException,
        ):
            llm_metrics.timeouts_total += 1
            logger.warning(
                "LLM stream timed out connection_id=%s",
                context.connection_id,
            )
            raise

        except asyncio.CancelledError:
            logger.info(
                "LLM stream cancelled connection_id=%s request_id=%s",
                context.connection_id,
                request.request_id,
            )
            raise

        except Exception:
            llm_metrics.failures_total += 1
            logger.exception(
                "LLM stream failed connection_id=%s",
                context.connection_id,
            )
            raise

        finally:
            await self._unregister(
                connection_id=context.connection_id,
                request_id=request.request_id,
            )
