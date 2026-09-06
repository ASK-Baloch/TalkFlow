from __future__ import annotations

import asyncio
from pathlib import Path

import numpy as np
import soxr
import torch

from chatterbox.tts_turbo import (
    ChatterboxTurboTTS,
)

from .config import (
    WorkerSettings,
)


class ChatterboxRuntime:
    def __init__(
        self,
        settings: WorkerSettings,
    ) -> None:
        self.settings = settings

        self.model: (
            ChatterboxTurboTTS | None
        ) = None

        self._lock = asyncio.Lock()

    async def start(
        self,
    ) -> None:
        reference = Path(
            self.settings.reference_audio
        )

        if not reference.exists():
            raise FileNotFoundError(
                "Chatterbox reference audio "
                f"not found: {reference}"
            )

        if (
            self.settings.device == "cuda"
            and not torch.cuda.is_available()
        ):
            raise RuntimeError(
                "CUDA requested for Chatterbox "
                "but CUDA is unavailable"
            )

        self.model = await asyncio.to_thread(
            ChatterboxTurboTTS
            .from_pretrained,
            device=(
                self.settings.device
            ),
        )

        if (
            self.settings.warmup_enabled
        ):
            await self.synthesize(
                text="Hello.",
                voice_id=(
                    self.settings.voice_id
                ),
            )

    async def stop(
        self,
    ) -> None:
        self.model = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    async def synthesize(
        self,
        *,
        text: str,
        voice_id: str,
    ) -> bytes:
        if self.model is None:
            raise RuntimeError(
                "Chatterbox model is not loaded"
            )

        if (
            voice_id
            != self.settings.voice_id
        ):
            raise ValueError(
                f"Unknown voice_id: {voice_id}"
            )

        if len(text) > (
            self.settings.max_text_chars
        ):
            raise ValueError(
                "Text exceeds worker limit"
            )

        async with self._lock:
            wav = await asyncio.to_thread(
                self.model.generate,
                text,
                audio_prompt_path=(
                    self.settings
                    .reference_audio
                ),
            )

        audio = (
            wav.detach()
            .float()
            .cpu()
            .numpy()
            .reshape(-1)
            .astype(np.float32)
        )

        source_rate = int(
            self.model.sr
        )

        if (
            source_rate
            != self.settings
            .target_sample_rate
        ):
            audio = soxr.resample(
                audio,
                source_rate,
                self.settings
                .target_sample_rate,
                quality="HQ",
            )

        return self._to_pcm16(
            audio
        )

    @staticmethod
    def _to_pcm16(
        audio: np.ndarray,
    ) -> bytes:
        audio = np.asarray(
            audio,
            dtype=np.float32,
        )

        audio = np.nan_to_num(
            audio,
            nan=0.0,
            posinf=1.0,
            neginf=-1.0,
        )

        peak = (
            float(
                np.max(
                    np.abs(audio)
                )
            )
            if audio.size
            else 0.0
        )

        if peak > 0.98:
            audio *= (
                0.98 / peak
            )

        audio = np.clip(
            audio,
            -1.0,
            1.0,
        )

        return np.round(
            audio * 32767.0
        ).astype(
            "<i2"
        ).tobytes()