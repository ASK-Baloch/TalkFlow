from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class RecordingStatus(
    str,
    Enum,
):
    PENDING = "PENDING"

    WAITING_FOR_SOURCE = "WAITING_FOR_SOURCE"

    FETCHING = "FETCHING"

    VALIDATING = "VALIDATING"

    STORING = "STORING"

    READY = "READY"

    FAILED = "FAILED"


@dataclass(slots=True)
class RecordingRequest:
    call_id: str

    ended_at: datetime


@dataclass(slots=True)
class RecordingFileInfo:
    path: Path

    size_bytes: int

    duration_ms: int

    sample_rate: int

    channels: int

    sample_width_bytes: int

    frame_count: int

    sha256: str


@dataclass(slots=True)
class StoredRecording:
    provider: str

    storage_key: str

    size_bytes: int
