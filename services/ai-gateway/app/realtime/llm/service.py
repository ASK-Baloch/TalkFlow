from __future__ import annotations

import asyncio
import logging
from uuid import uuid4

import httpx

from app.realtime.providers.llm import (
    LLMProvider,
    LLMRequest,
)

from .fallback import (
    build_fallback_messages,
)
from .metrics import (
    llm_metrics,
)
from .types import (
    LLMFallbackContext,
    LLMFallbackResult,
)

logger = logging.getLogger("talkflow.llm")


class LLMService:
    def __init__(
        self,
        *,
        provider: LLMProvider,
        enabled: bool,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
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

    async def start(
        self,
    ) -> None:
        if not self.enabled:
            return

        await self.provider.start()

    async def stop(
        self,
    ) -> None:
        if not self.enabled:
            return

        await self.provider.stop()

    async def health(
        self,
    ) -> dict:
        if not self.enabled:
            return {
                "enabled": False,
                "ready": True,
            }

        provider_health = await self.provider.health()

        return {
            "enabled": True,
            "provider": (provider_health),
        }

    async def generate_fallback(
        self,
        context: LLMFallbackContext,
    ) -> LLMFallbackResult | None:
        if not self.enabled:
            llm_metrics.fallback_skipped_total += 1

            return None

        messages = build_fallback_messages(
            context,
            max_history_turns=(self.max_history_turns),
            max_input_chars=(self.max_input_chars),
        )

        request = LLMRequest(
            messages=messages,
            request_id=str(uuid4()),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            presence_penalty=(self.presence_penalty),
            enable_thinking=(self.enable_thinking),
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

        except Exception:
            llm_metrics.failures_total += 1

            logger.exception(
                "LLM request failed connection_id=%s",
                context.connection_id,
            )

            return None

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
