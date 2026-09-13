from __future__ import annotations

import hashlib
import wave
from pathlib import Path

from .types import (
    RecordingFileInfo,
)


def calculate_sha256(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def validate_wav(
    path: Path,
    *,
    max_file_bytes: int,
) -> RecordingFileInfo:
    if not path.exists():
        raise FileNotFoundError(path)

    size_bytes = path.stat().st_size

    if size_bytes <= 44:
        raise ValueError("WAV is empty or too small")

    if size_bytes > max_file_bytes:
        raise ValueError("Recording exceeds maximum configured size")

    with wave.open(
        str(path),
        "rb",
    ) as wav:
        channels = wav.getnchannels()

        sample_width = wav.getsampwidth()

        sample_rate = wav.getframerate()

        frame_count = wav.getnframes()

    if channels not in {
        1,
        2,
    }:
        raise ValueError(f"Unsupported recording channel count: {channels}")

    if sample_width not in {
        1,
        2,
        3,
        4,
    }:
        raise ValueError("Unsupported WAV sample width")

    if sample_rate <= 0:
        raise ValueError("Invalid WAV sample rate")

    if frame_count <= 0:
        raise ValueError("Recording has no frames")

    duration_ms = int((frame_count / sample_rate) * 1000)

    return RecordingFileInfo(
        path=path,
        size_bytes=(size_bytes),
        duration_ms=(duration_ms),
        sample_rate=(sample_rate),
        channels=channels,
        sample_width_bytes=(sample_width),
        frame_count=(frame_count),
        sha256=(calculate_sha256(path)),
    )
