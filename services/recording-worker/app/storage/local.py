from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from app.storage.base import (
    RecordingStorageProvider,
)
from app.types import (
    StoredRecording,
)


class LocalRecordingStorage(RecordingStorageProvider):
    def __init__(
        self,
        *,
        root: str,
    ) -> None:
        self.root = Path(root)

    async def store(
        self,
        *,
        call_id: str,
        source: Path,
    ) -> StoredRecording:
        destination = self.root / call_id[:2] / f"{call_id}.wav"

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        await asyncio.to_thread(
            shutil.copy2,
            source,
            destination,
        )

        return StoredRecording(
            provider="local",
            storage_key=(str(destination)),
            size_bytes=(destination.stat().st_size),
        )
