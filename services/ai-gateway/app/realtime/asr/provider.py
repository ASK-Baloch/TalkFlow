from app.realtime.providers.stt import (
    STTProvider,
    STTResult,
)

# Backwards-compatible Phase 3 names.
AsrProvider = STTProvider
AsrDecodeResult = STTResult


__all__ = [
    "AsrDecodeResult",
    "AsrProvider",
]
