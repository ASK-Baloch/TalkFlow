import asyncio

from app.realtime.tts.interruption import (
    PlaybackGeneration,
)


def test_old_generation_becomes_stale():
    async def run():
        generation = PlaybackGeneration(connection_id="call-1")

        request_generation = await generation.current()

        assert request_generation == 0

        await generation.advance()

        assert not (await generation.is_current(request_generation))

    asyncio.run(run())
