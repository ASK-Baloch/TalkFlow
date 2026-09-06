from __future__ import annotations

from typing import Any

import numpy as np
from faster_whisper import WhisperModel

from .stt import (
    STTProvider,
    STTResult,
)


class FasterWhisperSTTProvider(
    STTProvider
):
    provider_name = "faster_whisper"

    def __init__(
        self,
        *,
        model_name: str,
        device: str,
        compute_type: str,
        language: str | None,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.language = language

        self.model: WhisperModel | None = (
            None
        )

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> FasterWhisperSTTProvider:
        return cls(
            model_name=(
                settings.asr_model
            ),
            device=(
                settings.asr_device
            ),
            compute_type=(
                settings.asr_compute_type
            ),
            language=(
                settings.asr_language
            ),
        )

    async def start(
        self,
    ) -> None:
        if self.model is not None:
            return

        self.model = WhisperModel(
            self.model_name,
            device=self.device,
            compute_type=(
                self.compute_type
            ),
        )

    async def stop(
        self,
    ) -> None:
        self.model = None

    def transcribe(
        self,
        audio: np.ndarray,
        *,
        beam_size: int = 1,
    ) -> STTResult:
        if self.model is None:
            raise RuntimeError(
                "Faster-Whisper provider "
                "has not been started"
            )

        segments, info = (
            self.model.transcribe(
                audio,
                language=self.language,
                beam_size=beam_size,
                vad_filter=False,
                condition_on_previous_text=False,
                word_timestamps=False,
            )
        )

        # Faster-Whisper performs actual decoding while
        # consuming its segment iterator.
        segments = list(
            segments
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        return STTResult(
            text=text,
            language=getattr(
                info,
                "language",
                None,
            ),
            language_probability=getattr(
                info,
                "language_probability",
                None,
            ),
        )

    async def health(
        self,
    ) -> dict[str, Any]:
        return {
            "provider": (
                self.provider_name
            ),
            "model": self.model_name,
            "device": self.device,
            "compute_type": (
                self.compute_type
            ),
            "ready": (
                self.model is not None
            ),
        }


# Compatibility alias for Phase 3 code that may
# still import FasterWhisperProvider.
FasterWhisperProvider = (
    FasterWhisperSTTProvider
)