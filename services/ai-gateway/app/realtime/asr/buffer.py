from __future__ import annotations

from collections import deque

import numpy as np


class AudioRingBuffer:
    def __init__(
        self,
        *,
        sample_rate: int,
        max_ms: int,
    ):
        self.sample_rate = sample_rate

        self.max_samples = int(sample_rate * max_ms / 1000)

        self._chunks: deque[np.ndarray] = deque()

        self._samples = 0

    def append(
        self,
        audio: np.ndarray,
    ):
        if audio.size == 0:
            return

        self._chunks.append(audio.copy())

        self._samples += audio.size

        while self._samples > self.max_samples and self._chunks:
            excess = self._samples - self.max_samples

            first = self._chunks[0]

            if first.size <= excess:
                self._chunks.popleft()
                self._samples -= first.size

            else:
                self._chunks[0] = first[excess:]

                self._samples -= excess

    def snapshot(
        self,
    ) -> np.ndarray:
        if not self._chunks:
            return np.empty(
                0,
                dtype=np.float32,
            )

        return np.concatenate(list(self._chunks))

    def clear(self):
        self._chunks.clear()
        self._samples = 0


class UtteranceBuffer:
    def __init__(self):
        self._chunks = []
        self.samples = 0

    def append(
        self,
        audio: np.ndarray,
    ):
        if audio.size:
            self._chunks.append(audio.copy())

            self.samples += audio.size

    def snapshot(
        self,
    ) -> np.ndarray:
        if not self._chunks:
            return np.empty(
                0,
                dtype=np.float32,
            )

        return np.concatenate(self._chunks)

    def clear(self):
        self._chunks.clear()
        self.samples = 0
