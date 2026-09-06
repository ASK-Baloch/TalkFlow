from __future__ import annotations

from typing import Any

import numpy as np

from .stt import (
    STTProvider,
    STTResult,
)


class DummySTTProvider(
    STTProvider
):
    provider_name = "dummy"

    def __init__(
        self,
        *,
        text: str,
    ) -> None:
        self.text = text

    @classmethod
    def from_settings(
        cls,
        settings: Any,
    ) -> DummySTTProvider:
        text = getattr(
            settings,
            "stt_dummy_text",
            "This is a dummy transcript.",
        )

        return cls(
            text=text
        )

    def transcribe(
        self,
        audio: np.ndarray,
        *,
        beam_size: int = 1,
    ) -> STTResult:
        del audio
        del beam_size

        return STTResult(
            text=self.text,
            language="en",
            language_probability=1.0,
        )