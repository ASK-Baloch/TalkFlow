import numpy as np

from app.realtime.vad.audio import (
    Pcm16Chunker,
    pcm16le_to_float32,
)


def test_pcm16_conversion():
    samples = np.array(
        [
            -32768,
            0,
            32767,
        ],
        dtype="<i2",
    )

    audio = pcm16le_to_float32(samples.tobytes())

    assert audio.dtype == np.float32

    assert audio[0] == -1.0
    assert audio[1] == 0.0

    assert 0.99 < audio[2] < 1.0


def test_chunker_handles_arbitrary_boundaries():
    chunker = Pcm16Chunker(chunk_samples=256)

    # 320 bytes first.
    result = chunker.feed(b"\x00\x00" * 160)

    assert result == []

    # Another 320 bytes.
    result = chunker.feed(b"\x00\x00" * 160)

    assert len(result) == 1
    assert len(result[0]) == 512

    # 128 bytes should remain.
    assert chunker.buffered_bytes == 128
