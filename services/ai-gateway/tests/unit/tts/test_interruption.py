import asyncio

from app.realtime.tts.interruption import (
    PlaybackGeneration,
)


def test_generation_advances():
    async def run():
        generation = PlaybackGeneration(connection_id="call-1")

        assert await generation.current() == 0

        assert await generation.is_current(0)

        new_value = await generation.advance()

        assert new_value == 1

        assert not (await generation.is_current(0))

        assert await generation.is_current(1)

    asyncio.run(run())
