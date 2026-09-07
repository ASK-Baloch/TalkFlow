import asyncio

from app.realtime.providers.tts import (
    TTSAudioChunk,
)
from app.realtime.tts.playback import (
    AudioSocketPcmPlayer,
    PlaybackInterrupted,
)


class FakeWriter:
    def __init__(self):
        self.writes = []

    def write(
        self,
        data: bytes,
    ):
        self.writes.append(data)

    async def drain(
        self,
    ):
        return None


async def chunks():
    for _ in range(100):
        yield TTSAudioChunk(
            pcm=b"\x00" * 320,
            sample_rate=8000,
            channels=1,
            sample_width_bytes=2,
        )


def test_playback_interrupts():
    async def run():
        player = AudioSocketPcmPlayer(
            sample_rate=8000,
            sample_width_bytes=2,
            frame_ms=20,
        )

        writer = FakeWriter()

        allowed = True

        async def should_continue():
            return allowed

        task = asyncio.create_task(
            player.play_chunks(
                writer=writer,
                chunks=chunks(),
                should_continue=(should_continue),
            )
        )

        await asyncio.sleep(0.06)

        nonlocal_allowed[0] = False

        try:
            await task

        except PlaybackInterrupted:
            pass

        assert len(writer.writes) < 100

    nonlocal_allowed = [True]

    async def run_fixed():
        player = AudioSocketPcmPlayer(
            sample_rate=8000,
            sample_width_bytes=2,
            frame_ms=20,
        )

        writer = FakeWriter()

        async def should_continue():
            return nonlocal_allowed[0]

        task = asyncio.create_task(
            player.play_chunks(
                writer=writer,
                chunks=chunks(),
                should_continue=(should_continue),
            )
        )

        await asyncio.sleep(0.06)

        nonlocal_allowed[0] = False

        try:
            await task

        except PlaybackInterrupted:
            pass

        assert len(writer.writes) < 100

    asyncio.run(run_fixed())
