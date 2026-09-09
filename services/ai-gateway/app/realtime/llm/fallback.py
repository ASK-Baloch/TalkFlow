from __future__ import annotations

from app.realtime.providers.llm import (
    LLMMessage,
)

from .prompts import (
    TALKFLOW_SYSTEM_PROMPT,
    build_turn_instruction,
)
from .types import (
    LLMFallbackContext,
)


def build_fallback_messages(
    context: LLMFallbackContext,
    *,
    max_history_turns: int,
    max_input_chars: int,
) -> list[LLMMessage]:
    caller_text = context.caller_text.strip()

    if len(caller_text) > (max_input_chars):
        caller_text = caller_text[:max_input_chars]

    messages = [
        LLMMessage(
            role="system",
            content=(TALKFLOW_SYSTEM_PROMPT),
        )
    ]

    history = context.history[-max_history_turns:]

    for turn in history:
        if turn.role not in {
            "user",
            "assistant",
        }:
            continue

        text = turn.text.strip()

        if not text:
            continue

        messages.append(
            LLMMessage(
                role=turn.role,
                content=text[:max_input_chars],
            )
        )

    messages.append(
        LLMMessage(
            role="user",
            content=build_turn_instruction(
                caller_text=caller_text,
                current_state=(context.current_state),
                expected_field=(context.expected_field),
            ),
        )
    )

    return messages
