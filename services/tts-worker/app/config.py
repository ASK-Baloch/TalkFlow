from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(
    name: str,
    default: bool,
) -> bool:
    value = os.getenv(
        name
    )

    if value is None:
        return default

    return value.lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True)
class WorkerSettings:
    host: str = os.getenv(
        "TTS_WORKER_HOST",
        "127.0.0.1",
    )

    port: int = int(
        os.getenv(
            "TTS_WORKER_PORT",
            "8091",
        )
    )

    device: str = os.getenv(
        "TTS_WORKER_DEVICE",
        "cuda",
    )

    voice_id: str = os.getenv(
        "TTS_WORKER_VOICE_ID",
        "talkflow_primary",
    )

    reference_audio: str = os.getenv(
        "TTS_WORKER_REFERENCE_AUDIO",
        "tools/tts-assets/reference/"
        "talkflow_reference.wav",
    )

    target_sample_rate: int = int(
        os.getenv(
            "TTS_WORKER_TARGET_SAMPLE_RATE",
            "8000",
        )
    )

    warmup_enabled: bool = _bool(
        "TTS_WORKER_WARMUP_ENABLED",
        True,
    )

    max_text_chars: int = int(
        os.getenv(
            "TTS_WORKER_MAX_TEXT_CHARS",
            "500",
        )
    )


settings = WorkerSettings()