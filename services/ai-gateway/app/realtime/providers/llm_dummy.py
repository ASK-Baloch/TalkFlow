from __future__ import annotations

from time import perf_counter
from typing import Any

from .llm import (
    LLMProvider,
    LLMRequest,
    LLMResult,
)


class DummyLLMProvider(LLMProvider):
    provider_name = "dummy"

    def __init__(
        self,
        *,
        response: str,
    ) -> None:
        self.response = response

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> DummyLLMProvider:
        return cls(
            response=getattr(
                settings,
                "llm_dummy_response",
                (
                    "I can help with that. "
                    "Let's continue with the "
                    "qualification questions."
                ),
            )
        )

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResult:
        del request

        started = perf_counter()

        return LLMResult(
            text=self.response,
            model="dummy",
            finish_reason="stop",
            latency_ms=(perf_counter() - started) * 1000.0,
        )
