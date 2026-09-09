from app.realtime.llm.fallback import (
    build_fallback_messages,
)
from app.realtime.llm.types import (
    ConversationTurn,
    LLMFallbackContext,
)


def test_history_is_bounded():
    history = [
        ConversationTurn(
            role="user",
            text=f"user-{index}",
        )
        for index in range(20)
    ]

    context = LLMFallbackContext(
        connection_id="call-1",
        caller_text="What?",
        current_state=("COLLECTING_AGE"),
        expected_field="age",
        history=history,
    )

    messages = build_fallback_messages(
        context,
        max_history_turns=4,
        max_input_chars=2000,
    )

    # system + 4 history + current user
    assert len(messages) == 6
