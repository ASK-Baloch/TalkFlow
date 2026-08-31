import numpy as np
import pytest

from app.core.config import get_settings
from app.realtime.asr.faster_whisper import FasterWhisperProvider


@pytest.mark.gpu
def test_faster_whisper_smoke():
    settings = get_settings()

    provider = FasterWhisperProvider(
        model_name=settings.asr_model,
        device="cpu",
        compute_type="int8",
        language=settings.asr_language,
        condition_on_previous_text=False,
        word_timestamps=False,
        initial_prompt=settings.asr_initial_prompt,
    )

    # 1 second of silence
    audio = np.zeros(16000, dtype=np.float32)

    result = provider.transcribe(audio, beam_size=1)

    assert result is not None
    assert hasattr(result, "text")
