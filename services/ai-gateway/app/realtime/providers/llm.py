from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LLMMessage:
    role: str
    content: str


@dataclass(slots=True)
class LLMRequest:
    messages: list[LLMMessage]

    request_id: str | None = None

    max_tokens: int = 80

    temperature: float = 0.3

    top_p: float = 0.8

    top_k: int | None = None

    presence_penalty: float = 0.3

    enable_thinking: bool = False


@dataclass(slots=True)
class LLMStreamChunk:
    text: str

    request_id: str | None = None

    is_final: bool = False

    finish_reason: str | None = None


@dataclass(slots=True)
class LLMResult:
    text: str

    model: str | None = None

    finish_reason: str | None = None

    prompt_tokens: int | None = None

    completion_tokens: int | None = None

    total_tokens: int | None = None

    latency_ms: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    provider_name: str = "unknown"

    supports_streaming: bool = False

    supports_cancellation: bool = False

    @classmethod
    @abstractmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> LLMProvider:
        raise NotImplementedError

    async def start(
        self,
    ) -> None:
        return None

    async def stop(
        self,
    ) -> None:
        return None

    async def health(
        self,
    ) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "ready": True,
        }

    @abstractmethod
    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResult:
        raise NotImplementedError

    async def stream(
        self,
        request: LLMRequest,
    ) -> AsyncIterator[LLMStreamChunk]:
        result = await self.generate(request)

        yield LLMStreamChunk(
            text=result.text,
            request_id=request.request_id,
            is_final=True,
            finish_reason=(result.finish_reason),
        )

    async def cancel(
        self,
        request_id: str,
    ) -> bool:
        del request_id
        return False
