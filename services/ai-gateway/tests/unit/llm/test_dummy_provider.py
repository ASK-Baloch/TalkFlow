import asyncio

from app.realtime.providers.llm import (
    LLMMessage,
    LLMRequest,
)
from app.realtime.providers.llm_dummy import (
    DummyLLMProvider,
)


class Settings:
    llm_dummy_response = "Let's continue."


def test_dummy_llm():
    async def run():
        provider = DummyLLMProvider.from_settings(Settings())

        result = await provider.generate(
            LLMRequest(
                messages=[
                    LLMMessage(
                        role="user",
                        content="Hello",
                    )
                ]
            )
        )

        assert result.text == "Let's continue."

    asyncio.run(run())
