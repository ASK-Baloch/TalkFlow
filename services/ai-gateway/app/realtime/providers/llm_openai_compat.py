from __future__ import annotations

import json
import re
from time import perf_counter
from typing import Any

import httpx

from .llm import (
    LLMProvider,
    LLMRequest,
    LLMResult,
    LLMStreamChunk,
)


class OpenAICompatibleLLMProvider(LLMProvider):
    provider_name = "openai_compatible"

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float,
        supports_thinking: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")

        self.api_key = api_key

        self.model = model

        self.timeout_seconds = timeout_seconds

        self.supports_thinking = supports_thinking

        self.client: httpx.AsyncClient | None = None

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> OpenAICompatibleLLMProvider:
        return cls(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            timeout_seconds=(settings.llm_timeout_seconds),
            supports_thinking=getattr(settings, "llm_supports_thinking", False),
        )

    async def start(
        self,
    ) -> None:
        if self.client is not None:
            return

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_seconds),
            headers={
                "Authorization": (f"Bearer {self.api_key}"),
                "Content-Type": ("application/json"),
            },
        )

    async def stop(
        self,
    ) -> None:
        if self.client is None:
            return

        await self.client.aclose()

        self.client = None

    async def health(
        self,
    ) -> dict[str, Any]:
        if self.client is None:
            return {
                "provider": (self.provider_name),
                "model": self.model,
                "ready": False,
            }

        try:
            response = await self.client.get(f"{self.base_url}/models")

            response.raise_for_status()

            return {
                "provider": (self.provider_name),
                "model": self.model,
                "ready": True,
            }

        except Exception as exc:
            return {
                "provider": (self.provider_name),
                "model": self.model,
                "ready": False,
                "error": str(exc),
            }

    def _build_payload(self, request: LLMRequest) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": message.role,
                    "content": (message.content),
                }
                for message in request.messages
            ],
            "max_tokens": (request.max_tokens),
            "temperature": (request.temperature),
            "top_p": (request.top_p),
            "presence_penalty": (request.presence_penalty),
        }

        if request.top_k is not None:
            payload["top_k"] = request.top_k

        if self.supports_thinking:
            payload["chat_template_kwargs"] = {
                "enable_thinking": request.enable_thinking
            }

        return payload

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResult:
        if self.client is None:
            raise RuntimeError("LLM provider has not been started")

        payload = self._build_payload(request)

        started = perf_counter()

        response = await self.client.post(
            (f"{self.base_url}/chat/completions"),
            json=payload,
        )

        response.raise_for_status()

        latency_ms = (perf_counter() - started) * 1000.0

        data = response.json()

        choices = data.get(
            "choices",
            [],
        )

        if not choices:
            raise RuntimeError("LLM response contained no choices")

        choice = choices[0]

        message = choice.get(
            "message",
            {},
        )

        content = (message.get("content") or "").strip()

        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.DOTALL,
        ).strip()

        if not content:
            raise RuntimeError("LLM response was empty")

        usage = data.get(
            "usage",
            {},
        )

        return LLMResult(
            text=content,
            model=data.get(
                "model",
                self.model,
            ),
            finish_reason=choice.get("finish_reason"),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            latency_ms=latency_ms,
            metadata={"request_id": (request.request_id)},
        )

    async def stream(
        self,
        request: LLMRequest,
    ):
        if self.client is None:
            raise RuntimeError("LLM provider has not been started")

        payload = self._build_payload(request)

        payload["stream"] = True

        async with self.client.stream(
            "POST",
            (f"{self.base_url}/chat/completions"),
            json=payload,
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line:
                    continue

                if not line.startswith("data:"):
                    continue

                data = line[5:].strip()

                if data == "[DONE]":
                    yield LLMStreamChunk(
                        text="",
                        request_id=(request.request_id),
                        is_final=True,
                    )
                    return

                payload = json.loads(data)

                choices = payload.get(
                    "choices",
                    [],
                )

                if not choices:
                    continue

                choice = choices[0]

                delta = choice.get(
                    "delta",
                    {},
                )

                text = delta.get("content") or ""

                finish_reason = choice.get("finish_reason")

                if text:
                    yield LLMStreamChunk(
                        text=text,
                        request_id=(request.request_id),
                        is_final=False,
                        finish_reason=(finish_reason),
                    )

                if finish_reason:
                    yield LLMStreamChunk(
                        text="",
                        request_id=(request.request_id),
                        is_final=True,
                        finish_reason=(finish_reason),
                    )

                    return
