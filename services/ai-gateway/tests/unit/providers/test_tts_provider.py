import asyncio

from app.realtime.providers.tts import (
    TTSRequest,
)
from app.realtime.providers.tts_dummy import (
    DummyTTSProvider,
)


class Settings:
    tts_sample_rate = 8000
    tts_frame_ms = 20
    tts_dummy_frames = 5


def test_dummy_tts_provider():
    async def run():
        provider = (
            DummyTTSProvider
            .from_settings(
                Settings()
            )
        )

        await provider.start()

        chunks = []

        async for chunk in (
            provider.stream(
                TTSRequest(
                    text="hello"
                )
            )
        ):
            chunks.append(
                chunk
            )

        await provider.stop()

        assert len(chunks) == 5

        assert all(
            chunk.sample_rate
            == 8000
            for chunk
            in chunks
        )

        assert all(
            len(chunk.pcm)
            == 320
            for chunk
            in chunks
        )

    asyncio.run(
        run()
    )