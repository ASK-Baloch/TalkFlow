from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.types import (
    StoredRecording,
)


class RecordingStorageProvider(ABC):
    @abstractmethod
    async def store(
        self,
        *,
        call_id: str,
        source: Path,
    ) -> StoredRecording:
        raise NotImplementedError
