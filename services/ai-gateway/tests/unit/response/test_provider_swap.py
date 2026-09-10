import pytest

from app.realtime.llm.service import LLMService
from app.realtime.llm.types import LLMFallbackContext
from app.realtime.providers.llm_dummy import DummyLLMProvider


@pytest.mark.asyncio
async def test_provider_stream_fallback_wrapping():
    provider = DummyLLMProvider(response="This is a dummy response.")

    service = LLMService(
        enabled=True,
        provider=provider,
        max_tokens=80,
        temperature=0.3,
        top_p=0.8,
        top_k=None,
        presence_penalty=0.0,
        enable_thinking=False,
        max_history_turns=10,
        max_input_chars=1000,
    )

    context = LLMFallbackContext(
        connection_id="call-1",
        caller_text="Hello",
        current_state="start",
        history=[],
    )

    chunks = []

    async for chunk in service.stream_fallback(context):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert chunks[0].text == "This is a dummy response."
    assert chunks[0].is_final is True
