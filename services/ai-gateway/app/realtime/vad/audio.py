from __future__ import annotations

import numpy as np

PCM16_BYTES_PER_SAMPLE = 2


class PcmFormatError(ValueError):
    pass


def pcm16le_to_float32(payload: bytes) -> np.ndarray:
    """
    Convert little-endian signed PCM16 bytes into mono float32 [-1, 1).

    AudioSocket signed-linear PCM is handled without WAV/base64/disk
    conversion.
    """

    if len(payload) % PCM16_BYTES_PER_SAMPLE != 0:
        raise PcmFormatError(
            f"PCM16 payload must contain an even number of bytes, "
            f"received {len(payload)}"
        )

    samples = np.frombuffer(
        payload,
        dtype="<i2",
    )

    return (
        samples.astype(
            np.float32,
            copy=False,
        )
        / 32768.0
    )


class Pcm16Chunker:
    """
    Accept arbitrary AudioSocket payload boundaries and emit fixed-size
    Silero chunks.

    Never assume one TCP/AudioSocket packet equals one VAD inference.
    """

    def __init__(
        self,
        chunk_samples: int,
    ) -> None:
        if chunk_samples <= 0:
            raise ValueError("chunk_samples must be > 0")

        self.chunk_samples = chunk_samples
        self.chunk_bytes = chunk_samples * PCM16_BYTES_PER_SAMPLE

        self._buffer = bytearray()

    @property
    def buffered_bytes(self) -> int:
        return len(self._buffer)

    def feed(
        self,
        payload: bytes,
    ) -> list[bytes]:
        if len(payload) % PCM16_BYTES_PER_SAMPLE != 0:
            raise PcmFormatError("AudioSocket PCM16 payload had odd byte length")

        self._buffer.extend(payload)

        chunks: list[bytes] = []

        while len(self._buffer) >= self.chunk_bytes:
            chunks.append(bytes(self._buffer[: self.chunk_bytes]))

            del self._buffer[: self.chunk_bytes]

        return chunks

    def reset(self) -> None:
        self._buffer.clear()
