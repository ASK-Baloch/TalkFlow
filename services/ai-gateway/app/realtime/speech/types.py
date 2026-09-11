from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SpeechNormalizationContext:
    language: str = "en-US"

    expected_field: str | None = None

    provider_name: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NormalizedSpeech:
    display_text: str

    tts_text: str

    changed: bool

    rules_applied: list[str] = field(default_factory=list)
