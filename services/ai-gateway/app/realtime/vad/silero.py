from __future__ import annotations

import numpy as np
import torch
from silero_vad import load_silero_vad


class SileroVadEngine:
    """
    One persistent Silero model instance.

    Important:
    Silero keeps recurrent inference state internally, so an engine
    instance must not be shared concurrently between independent calls.
    """

    def __init__(
        self,
        *,
        sample_rate: int,
        use_onnx: bool = True,
    ) -> None:
        if sample_rate not in (8000, 16000):
            raise ValueError("Silero VAD supports 8000 or 16000 Hz")

        self.sample_rate = sample_rate

        self.model = load_silero_vad(
            onnx=use_onnx,
        )

        self.reset()

    def reset(self) -> None:
        self.model.reset_states()

    def probability(
        self,
        audio: np.ndarray,
    ) -> float:
        expected_samples = 256 if self.sample_rate == 8000 else 512

        if audio.ndim != 1:
            raise ValueError(f"VAD input must be mono 1-D, got {audio.shape}")

        if len(audio) != expected_samples:
            raise ValueError(
                f"Expected {expected_samples} samples, received {len(audio)}"
            )

        tensor = torch.from_numpy(
            np.ascontiguousarray(
                audio,
                dtype=np.float32,
            )
        )

        probability = self.model(
            tensor,
            self.sample_rate,
        ).item()

        return float(probability)
