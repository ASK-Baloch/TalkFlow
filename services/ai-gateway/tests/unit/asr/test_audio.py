import numpy as np

from app.realtime.asr.audio import (
    StreamingResampler,
)
from app.realtime.asr.buffer import AudioRingBuffer


def test_8k_to_16k_resampling():
    resampler = StreamingResampler(
        input_rate=8000,
        output_rate=16000,
    )

    audio = np.zeros(
        800,
        dtype=np.float32,
    )

    output = resampler.process(audio)

    assert output.dtype == np.float32


def test_pre_roll_keeps_recent_audio():
    ring = AudioRingBuffer(
        sample_rate=16000,
        max_ms=320,
    )

    ring.append(
        np.ones(
            16000,
            dtype=np.float32,
        )
    )

    snapshot = ring.snapshot()

    assert snapshot.size <= int(16000 * 0.320)
