from pathlib import Path

import pytest

from app.validator import (
    validate_wav,
)


def test_invalid_wav(
    tmp_path: Path,
):
    path = tmp_path / "invalid.wav"

    path.write_bytes(b"not-a-wave-file")

    with pytest.raises(ValueError):
        validate_wav(
            path,
            max_file_bytes=(1024 * 1024),
        )
