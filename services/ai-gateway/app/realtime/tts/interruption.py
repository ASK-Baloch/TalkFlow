from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from time import perf_counter_ns


@dataclass(slots=True)
class PlaybackGeneration:
    connection_id: str

    generation: int = 0

    interrupted_at_ns: int | None = None

    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def current(
        self,
    ) -> int:
        async with self.lock:
            return self.generation

    async def advance(
        self,
    ) -> int:
        async with self.lock:
            self.generation += 1

            self.interrupted_at_ns = perf_counter_ns()

            return self.generation

    async def is_current(
        self,
        generation: int,
    ) -> bool:
        async with self.lock:
            return generation == self.generation
