from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(slots=True)
class GenerationSnapshot:
    value: int


class ResponseGeneration:
    def __init__(self) -> None:
        self._value = 0
        self._lock = asyncio.Lock()

    async def current(
        self,
    ) -> GenerationSnapshot:
        async with self._lock:
            return GenerationSnapshot(value=self._value)

    async def advance(
        self,
    ) -> GenerationSnapshot:
        async with self._lock:
            self._value += 1

            return GenerationSnapshot(value=self._value)

    async def is_current(
        self,
        snapshot: GenerationSnapshot,
    ) -> bool:
        async with self._lock:
            return snapshot.value == self._value
