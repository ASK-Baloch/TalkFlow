import wave
from pathlib import Path

from app.validator import (
    validate_wav,
)


def test_valid_wav(
    tmp_path: Path,
):
    path = tmp_path / "test.wav"

    with wave.open(
        str(path),
        "wb",
    ) as wav:
        wav.setnchannels(1)

        wav.setsampwidth(2)

        wav.setframerate(8000)

        wav.writeframes(b"\x00\x00" * 8000)

    result = validate_wav(
        path,
        max_file_bytes=(10 * 1024 * 1024),
    )

    assert result.sample_rate == 8000

    assert result.channels == 1

    assert 990 <= result.duration_ms <= 1010

    assert len(result.sha256) == 64
