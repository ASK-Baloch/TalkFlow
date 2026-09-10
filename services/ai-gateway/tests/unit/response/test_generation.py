import asyncio

from app.realtime.response.generation import (
    ResponseGeneration,
)


def test_old_generation_becomes_stale():
    async def run():
        generation = ResponseGeneration()

        old = await generation.current()

        assert await generation.is_current(old)

        await generation.advance()

        assert not (await generation.is_current(old))

    asyncio.run(run())
