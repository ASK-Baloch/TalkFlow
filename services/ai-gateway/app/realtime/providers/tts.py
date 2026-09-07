from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
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
    provider_name: str = "unknown"

    supports_native_streaming: bool = False

    supports_cancellation: bool = False

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
            "provider": self.provider_name,
            "ready": True,
            "supports_native_streaming": (self.supports_native_streaming),
            "supports_cancellation": (self.supports_cancellation),
        }

    async def cancel(
        self,
        request_id: str,
    ) -> bool:
        del request_id

        return False

    @abstractmethod
    async def stream(
        self,
        request: TTSRequest,
    ) -> AsyncIterator[TTSAudioChunk]:
        raise NotImplementedError
