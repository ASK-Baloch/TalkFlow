from __future__ import annotations

from abc import ABC, abstractmethod
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

    temperature: float = 0.7

    top_p: float = 0.8

    top_k: int = 20

    presence_penalty: float = 0.3

    enable_thinking: bool = False


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
