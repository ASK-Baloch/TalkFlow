from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ConversationTurn:
    role: str
    text: str


@dataclass(slots=True)
class LLMFallbackContext:
    connection_id: str

    caller_text: str

    current_state: str

    expected_field: str | None = None

    history: list[ConversationTurn] = field(default_factory=list)

    speech_end_ms: float = 0.0


@dataclass(slots=True)
class LLMFallbackResult:
    text: str

    latency_ms: float

    model: str | None

    prompt_tokens: int | None = None

    completion_tokens: int | None = None

    total_tokens: int | None = None

    used_fallback: bool = True
