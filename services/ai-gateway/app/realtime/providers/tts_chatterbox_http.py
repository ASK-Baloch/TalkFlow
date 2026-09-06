from __future__ import annotations

from typing import (
    Any,
    AsyncIterator,
)

import httpx

from .tts import (
    TTSAudioChunk,
    TTSProvider,
    TTSRequest,
)


class ChatterboxHttpTTSProvider(
    TTSProvider
):
    provider_name = "chatterbox_http"

    # Current worker API streams transport chunks,
    # but the current official model.generate API
    # completes generation before those chunks exist.
    supports_native_streaming = False

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float,
        default_voice_id: str,
        frame_bytes: int,
    ) -> None:
        self.base_url = (
            base_url.rstrip("/")
        )

        self.timeout_seconds = (
            timeout_seconds
        )

        self.default_voice_id = (
            default_voice_id
        )

        self.frame_bytes = frame_bytes

        self.client: (
            httpx.AsyncClient | None
        ) = None

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> "ChatterboxHttpTTSProvider":
        samples_per_frame = int(
            settings.tts_sample_rate
            * settings.tts_frame_ms
            / 1000
        )

        return cls(
            base_url=(
                settings.tts_worker_url
            ),
            timeout_seconds=(
                settings
                .tts_worker_timeout_seconds
            ),
            default_voice_id=(
                settings
                .tts_default_voice_id
            ),
            frame_bytes=(
                samples_per_frame * 2
            ),
        )

    async def start(
        self,
    ) -> None:
        self.client = (
            httpx.AsyncClient(
                timeout=httpx.Timeout(
                    self.timeout_seconds
                )
            )
        )

    async def stop(
        self,
    ) -> None:
        if self.client is not None:
            await self.client.aclose()

            self.client = None

    async def health(
        self,
    ) -> dict[str, Any]:
        if self.client is None:
            return {
                "provider": (
                    self.provider_name
                ),
                "ready": False,
            }

        try:
            response = await self.client.get(
                f"{self.base_url}/health"
            )

            response.raise_for_status()

            data = response.json()

            return {
                "provider": (
                    self.provider_name
                ),
                "ready": bool(
                    data.get("ready")
                ),
                "worker": data,
                "supports_native_streaming": (
                    self
                    .supports_native_streaming
                ),
            }

        except Exception as exc:
            return {
                "provider": (
                    self.provider_name
                ),
                "ready": False,
                "error": str(exc),
            }

    async def stream(
        self,
        request: TTSRequest,
    ) -> AsyncIterator[
        TTSAudioChunk
    ]:
        if self.client is None:
            raise RuntimeError(
                "Chatterbox provider "
                "has not been started"
            )

        if not request.text:
            raise ValueError(
                "Dynamic TTS requires text"
            )

        payload = {
            "text": request.text,
            "voice_id": (
                request.voice_id
                or self.default_voice_id
            ),
        }

        buffer = bytearray()

        async with self.client.stream(
            "POST",
            f"{self.base_url}/v1/synthesize",
            json=payload,
        ) as response:
            response.raise_for_status()

            async for network_chunk in (
                response.aiter_bytes()
            ):
                buffer.extend(
                    network_chunk
                )

                while len(buffer) >= (
                    self.frame_bytes
                ):
                    frame = bytes(
                        buffer[
                            :self.frame_bytes
                        ]
                    )

                    del buffer[
                        :self.frame_bytes
                    ]

                    yield TTSAudioChunk(
                        pcm=frame,
                        sample_rate=8000,
                        channels=1,
                        sample_width_bytes=2,
                        is_final=False,
                    )

        if buffer:
            yield TTSAudioChunk(
                pcm=bytes(buffer),
                sample_rate=8000,
                channels=1,
                sample_width_bytes=2,
                is_final=True,
            )

        else:
            # Empty terminal chunk is unnecessary.
            return