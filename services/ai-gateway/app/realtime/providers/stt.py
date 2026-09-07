from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(slots=True)
class STTResult:
    text: str

    language: str | None = None

    language_probability: float | None = None


class STTProvider(ABC):
    """
    Stable TalkFlow STT contract.

    Any STT implementation must convert its vendor/model-specific
    output into STTResult.
    """

    provider_name: str = "unknown"

    @classmethod
    @abstractmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> STTProvider:
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
        }

    @abstractmethod
    def transcribe(
        self,
        audio: np.ndarray,
        *,
        beam_size: int = 1,
    ) -> STTResult:
        raise NotImplementedError
