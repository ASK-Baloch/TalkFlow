from __future__ import annotations

from collections.abc import AsyncIterator
from typing import (
    Any,
)

from app.realtime.tts.cache import (
    TtsAssetCache,
)

from .tts import (
    TTSAudioChunk,
    TTSProvider,
    TTSRequest,
)


class PregeneratedTTSProvider(TTSProvider):
    provider_name = "pregenerated"

    supports_native_streaming = True

    def __init__(
        self,
        *,
        cache: TtsAssetCache,
        frame_bytes: int,
    ) -> None:
        self.cache = cache
        self.frame_bytes = frame_bytes

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> PregeneratedTTSProvider:
        cache = TtsAssetCache(
            prefix=(settings.tts_cache_prefix),
            version=(settings.tts_asset_version),
            asset_dir=(settings.tts_asset_dir),
            cache_enabled=(settings.tts_cache_enabled),
            local_fallback=(settings.tts_cache_local_fallback),
        )

        samples_per_frame = int(settings.tts_sample_rate * settings.tts_frame_ms / 1000)

        return cls(
            cache=cache,
            frame_bytes=(samples_per_frame * 2),
        )

    async def start(
        self,
    ) -> None:
        await self.cache.start()

    async def stop(
        self,
    ) -> None:
        await self.cache.stop()

    async def stream(
        self,
        request: TTSRequest,
    ) -> AsyncIterator[TTSAudioChunk]:
        if not request.response_id:
            raise ValueError("Pregenerated TTS requires response_id")

        from app.realtime.tts.types import (
            ResponseId,
        )

        response_id = ResponseId(request.response_id)

        asset = await self.cache.get(response_id)

        offset = 0

        while offset < len(asset.pcm):
            chunk = asset.pcm[offset : offset + self.frame_bytes]

            offset += self.frame_bytes

            is_final = offset >= len(asset.pcm)

            yield TTSAudioChunk(
                pcm=chunk,
                sample_rate=(asset.sample_rate),
                channels=(asset.channels),
                sample_width_bytes=(asset.sample_width_bytes),
                is_final=is_final,
            )
