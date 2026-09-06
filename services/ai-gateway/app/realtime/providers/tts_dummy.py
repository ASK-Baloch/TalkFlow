from __future__ import annotations

from collections.abc import AsyncIterator
from typing import (
    Any,
)

from .tts import (
    TTSAudioChunk,
    TTSProvider,
    TTSRequest,
)


class DummyTTSProvider(
    TTSProvider
):
    provider_name = "dummy"

    supports_native_streaming = True

    def __init__(
        self,
        *,
        sample_rate: int,
        frame_ms: int,
        frames: int,
    ) -> None:
        self.sample_rate = sample_rate

        self.frame_ms = frame_ms

        self.frames = frames

        samples_per_frame = int(
            sample_rate
            * frame_ms
            / 1000
        )

        self.frame_bytes = (
            samples_per_frame
            * 2
        )

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> DummyTTSProvider:
        return cls(
            sample_rate=(
                settings.tts_sample_rate
            ),
            frame_ms=(
                settings.tts_frame_ms
            ),
            frames=getattr(
                settings,
                "tts_dummy_frames",
                10,
            ),
        )

    async def stream(
        self,
        request: TTSRequest,
    ) -> AsyncIterator[
        TTSAudioChunk
    ]:
        del request

        silence = bytes(
            self.frame_bytes
        )

        for index in range(
            self.frames
        ):
            yield TTSAudioChunk(
                pcm=silence,
                sample_rate=(
                    self.sample_rate
                ),
                channels=1,
                sample_width_bytes=2,
                is_final=(
                    index
                    == self.frames - 1
                ),
            )