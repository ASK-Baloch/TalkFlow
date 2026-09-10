import asyncio

import pytest

from app.realtime.conversation.turn_controller import ConversationTurnController
from app.realtime.llm.types import LLMFallbackContext
from app.realtime.providers.llm import LLMStreamChunk
from app.realtime.response.stream_assembler import (
    SentenceStreamAssembler,
    StreamAssemblerConfig,
)
from app.realtime.response.streaming import StreamingResponseOrchestrator


class FakeTTS:
    def __init__(self):
        self.enqueued = []

    async def enqueue(self, connection_id, planned, session_uuid, speech_end_ms=0.0):
        self.enqueued.append(planned.text)
        return True

    async def interrupt(self, connection_id):
        return True


class FakePlanner:
    class Planned:
        def __init__(self, text):
            self.text = text

    def plan_dynamic(self, text):
        return self.Planned(text)


class SlowFakeLLM:
    async def cancel(self, connection_id):
        return True

    async def stream_fallback(self, context):
        yield LLMStreamChunk(
            text="This is the first complete sentence that is long enough. T",
            is_final=False,
        )
        await asyncio.sleep(1)
        yield LLMStreamChunk(text="This sentence must never be spoken.", is_final=True)


@pytest.mark.asyncio
async def test_streaming_cancellation_drops_stale_segments():
    llm = SlowFakeLLM()
    tts = FakeTTS()
    planner = FakePlanner()

    orchestrator = StreamingResponseOrchestrator(
        llm_service=llm,
        response_planner=planner,
        tts_service=tts,
        assembler_factory=lambda: SentenceStreamAssembler(
            config=StreamAssemblerConfig(
                min_chars=10,
                target_chars=40,
                max_chars=100,
                min_words=2,
                allow_clause_boundaries=True,
            )
        ),
    )

    turn_controller = ConversationTurnController(
        llm_service=llm,
        tts_service=tts,
        response_orchestrator=orchestrator,
    )

    context = LLMFallbackContext(
        connection_id="call-1", caller_text="hello", current_state="start"
    )

    task = asyncio.create_task(
        orchestrator.generate_dynamic(
            context=context,
            session_uuid="uuid-1",
        )
    )

    # Let the first sentence yield and process
    await asyncio.sleep(0.1)

    # Interrupt the turn (simulating caller barge-in)
    await turn_controller.interrupt_turn(connection_id="call-1")

    # Wait for task to finish / cancel
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Verify that only the first sentence was enqueued
    assert tts.enqueued == ["This is the first complete sentence that is long enough."]
