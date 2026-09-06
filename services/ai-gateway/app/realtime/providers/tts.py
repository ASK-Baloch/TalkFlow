from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import (
    Any,
)


@dataclass(slots=True)
class TTSRequest:
    text: str | None = None

    response_id: str | None = None

    voice_id: str | None = None

    request_id: str | None = None


@dataclass(slots=True)
class TTSAudioChunk:
    pcm: bytes

    sample_rate: int = 8000

    channels: int = 1

    sample_width_bytes: int = 2

    is_final: bool = False


class TTSProvider(ABC):
    """
    Stable TalkFlow TTS interface.

    Provider implementations MUST emit telephony-ready
    signed PCM16 little-endian audio.
    """

    provider_name: str = "unknown"

    supports_native_streaming: bool = (
        False
    )

    @classmethod
    @abstractmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> TTSProvider:
        raise NotImplementedError

    async def start(
        self,
    ) -> None:
        return None

    async def stop(
        self,
    ) -> None:
        return None

    async def health(
        self,
    ) -> dict[str, Any]:
        return {
            "provider": (
                self.provider_name
            ),
            "ready": True,
            "supports_native_streaming": (
                self
                .supports_native_streaming
            ),
        }

    @abstractmethod
    async def stream(
        self,
        request: TTSRequest,
    ) -> AsyncIterator[
        TTSAudioChunk
    ]:
        """
        Produce telephony-ready PCM.

        The caller does not know whether audio comes from:
        - Redis
        - Chatterbox
        - an API
        - another local model
        - a mock provider
        """
        raise NotImplementedError