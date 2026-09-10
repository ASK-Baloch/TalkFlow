import asyncio

from app.realtime.conversation.turn_controller import (
    ConversationTurnController,
)


class BrokenLLMService:
    async def cancel(
        self,
        connection_id: str,
    ) -> bool:
        del connection_id

        raise RuntimeError("simulated LLM failure")


class WorkingTTSService:
    def __init__(self):
        self.calls = 0

    async def interrupt(
        self,
        connection_id: str,
    ) -> bool:
        del connection_id

        self.calls += 1

        return True


class WorkingResponseOrchestrator:
    def __init__(self):
        self.calls = 0

    async def interrupt(
        self,
        connection_id: str,
    ) -> bool:
        del connection_id
        self.calls += 1
        return True


def test_tts_still_interrupts_when_llm_cancel_fails():
    async def run():
        llm = BrokenLLMService()
        tts = WorkingTTSService()
        resp = WorkingResponseOrchestrator()

        controller = ConversationTurnController(
            llm_service=llm,
            tts_service=tts,
            response_orchestrator=resp,
        )

        result = await controller.interrupt_turn(connection_id="call-1")

        assert tts.calls == 1
        assert resp.calls == 1

        assert result.llm_cancelled is False

        assert result.tts_interrupted is True

        assert result.response_interrupted is True

    asyncio.run(run())


class WorkingLLMService:
    def __init__(self):
        self.calls = 0

    async def cancel(
        self,
        connection_id: str,
    ) -> bool:
        del connection_id
        self.calls += 1
        return True


class BrokenTTSService:
    async def interrupt(
        self,
        connection_id: str,
    ) -> bool:
        del connection_id
        raise RuntimeError("simulated TTS failure")


def test_llm_still_cancels_when_tts_interrupt_fails():
    async def run():
        llm = WorkingLLMService()
        tts = BrokenTTSService()
        resp = WorkingResponseOrchestrator()

        controller = ConversationTurnController(
            llm_service=llm,
            tts_service=tts,
            response_orchestrator=resp,
        )

        result = await controller.interrupt_turn(connection_id="call-2")

        assert llm.calls == 1
        assert resp.calls == 1

        assert result.llm_cancelled is True
        assert result.tts_interrupted is False
        assert result.response_interrupted is True

    asyncio.run(run())
