from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from .silero import SileroVadEngine


class VadCapacityError(RuntimeError):
    pass


class SileroVadPool:
    def __init__(
        self,
        *,
        sample_rate: int,
        use_onnx: bool,
        size: int,
        acquire_timeout_ms: int,
    ) -> None:
        if size < 1:
            raise ValueError("VAD pool size must be >= 1")

        self.sample_rate = sample_rate
        self.use_onnx = use_onnx
        self.size = size

        self.acquire_timeout_seconds = acquire_timeout_ms / 1000.0

        self._queue: asyncio.Queue[SileroVadEngine] = asyncio.Queue(maxsize=size)

        self._started = False

    @property
    def ready(self) -> bool:
        return self._started

    @property
    def available(self) -> int:
        return self._queue.qsize()

    async def start(self) -> None:
        if self._started:
            return

        for _ in range(self.size):
            engine = await asyncio.to_thread(
                SileroVadEngine,
                sample_rate=self.sample_rate,
                use_onnx=self.use_onnx,
            )

            self._queue.put_nowait(engine)

        self._started = True

    async def stop(self) -> None:
        while not self._queue.empty():
            self._queue.get_nowait()
            self._queue.task_done()

        self._started = False

    @asynccontextmanager
    async def lease(self):
        if not self._started:
            raise RuntimeError("VAD pool has not started")

        try:
            engine = await asyncio.wait_for(
                self._queue.get(),
                timeout=self.acquire_timeout_seconds,
            )
        except TimeoutError as exc:
            raise VadCapacityError("No VAD model instance available") from exc

        try:
            engine.reset()
            yield engine

        finally:
            engine.reset()

            self._queue.put_nowait(engine)
            self._queue.task_done()
