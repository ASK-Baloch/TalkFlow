from __future__ import annotations

import numpy as np
import soxr


def pcm16le_to_float32(
    payload: bytes,
) -> np.ndarray:
    if len(payload) % 2:
        raise ValueError("PCM16 payload must have even byte length")

    pcm = np.frombuffer(
        payload,
        dtype="<i2",
    )

    return (
        pcm.astype(
            np.float32,
            copy=False,
        )
        / 32768.0
    )


class StreamingResampler:
    def __init__(
        self,
        *,
        input_rate: int = 8000,
        output_rate: int = 16000,
    ):
        self.input_rate = input_rate
        self.output_rate = output_rate

        self._create_stream()

    def _create_stream(self):
        self._stream = soxr.ResampleStream(
            self.input_rate,
            self.output_rate,
            1,
            dtype="float32",
        )

    def process(
        self,
        audio: np.ndarray,
    ) -> np.ndarray:
        if audio.size == 0:
            return np.empty(
                0,
                dtype=np.float32,
            )

        return self._stream.resample_chunk(
            audio,
            last=False,
        )

    def reset(self):
        self._create_stream()
