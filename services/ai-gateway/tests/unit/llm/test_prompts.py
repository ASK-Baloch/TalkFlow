from app.realtime.llm.fallback import (
    build_fallback_messages,
)
from app.realtime.llm.types import (
    LLMFallbackContext,
)


def test_prompt_preserves_llm_boundaries():
    context = LLMFallbackContext(
        connection_id="call-1",
        caller_text=("Do I qualify for Medicare?"),
        current_state=("COLLECTING_PART_A"),
        expected_field=("Medicare Part A"),
    )

    messages = build_fallback_messages(
        context,
        max_history_turns=4,
        max_input_chars=2000,
    )

    system = messages[0].content

    assert "NOT the qualification engine" in system

    assert "Never decide whether the caller qualifies" in system
