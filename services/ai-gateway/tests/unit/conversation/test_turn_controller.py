import asyncio

from app.realtime.conversation.turn_controller import (
    ConversationTurnController,
)


class FakeLLMService:
    def __init__(self):
        self.cancelled = []

    async def cancel(
        self,
        connection_id: str,
    ) -> bool:
        self.cancelled.append(connection_id)

        return True


class FakeTTSService:
    def __init__(self):
        self.interrupted = []

    async def interrupt(
        self,
        connection_id: str,
    ) -> bool:
        self.interrupted.append(connection_id)

        return True


class FakeResponseOrchestrator:
    def __init__(self):
        self.interrupted = []

    async def interrupt(
        self,
        connection_id: str,
    ) -> bool:
        self.interrupted.append(connection_id)

        return True


def test_turn_controller_cancels_all_three():
    async def run():
        llm = FakeLLMService()
        tts = FakeTTSService()
        resp = FakeResponseOrchestrator()

        controller = ConversationTurnController(
            llm_service=llm,
            tts_service=tts,
            response_orchestrator=resp,
        )

        result = await controller.interrupt_turn(connection_id="call-1")

        assert llm.cancelled == ["call-1"]

        assert tts.interrupted == ["call-1"]

        assert resp.interrupted == ["call-1"]

        assert result.llm_cancelled is True

        assert result.tts_interrupted is True

        assert result.response_interrupted is True

    asyncio.run(run())
