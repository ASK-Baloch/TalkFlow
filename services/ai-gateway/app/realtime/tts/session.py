from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from .interruption import (
    PlaybackGeneration,
)
from .types import (
    PlaybackRequest,
)


@dataclass(slots=True)
class TtsCallSession:
    connection_id: str

    writer: asyncio.StreamWriter

    queue: asyncio.Queue[PlaybackRequest]

    generation: PlaybackGeneration

    worker_task: asyncio.Task | None = None

    current_playback_task: asyncio.Task | None = None

    current_request: PlaybackRequest | None = None

    playback_started_at: float | None = None

    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
