import numpy as np

from app.realtime.vad.silero import (
    SileroVadEngine,
)


def test_silero_processes_8k_chunk():
    engine = SileroVadEngine(
        sample_rate=8000,
        use_onnx=True,
    )

    silence = np.zeros(
        256,
        dtype=np.float32,
    )

    probability = engine.probability(silence)

    assert 0.0 <= probability <= 1.0
