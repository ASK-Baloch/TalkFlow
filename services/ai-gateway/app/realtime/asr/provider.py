from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class AsrDecodeResult:
    text: str

    language: str | None = None
    language_probability: float | None = None


class AsrStream(ABC):
    @abstractmethod
    def push_audio(self, audio: np.ndarray) -> None:
        """Push a chunk of 16kHz float32 audio into the stream."""
        raise NotImplementedError

    @abstractmethod
    def get_partial(self) -> AsrDecodeResult:
        """Get the current partial transcript from the stream."""
        raise NotImplementedError

    @abstractmethod
    def finalize(self) -> AsrDecodeResult:
        """Finalize the stream and return the final transcript."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the stream and release any state/resources."""
        raise NotImplementedError


class AsrProvider(ABC):
    @abstractmethod
    def open_stream(
        self, *, beam_size: int, context_hints: list[str] | None = None
    ) -> AsrStream:
        """Open a stateful ASR stream for continuous processing."""
        raise NotImplementedError

    @abstractmethod
    def transcribe(
        self,
        audio: np.ndarray,
        *,
        beam_size: int,
        context_hints: list[str] | None = None,
    ) -> AsrDecodeResult:
        """Offline transcription of a complete audio utterance."""
        raise NotImplementedError
