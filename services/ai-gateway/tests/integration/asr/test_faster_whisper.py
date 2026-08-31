from unittest import mock

import numpy as np
import pytest

from app.core.config import get_settings
from app.realtime.asr.faster_whisper import FasterWhisperProvider


@pytest.mark.gpu
@mock.patch("app.realtime.asr.faster_whisper.WhisperModel")
def test_faster_whisper_smoke(mock_whisper_model):
    # Setup mock behavior to avoid network calls to huggingface hub
    mock_model_instance = mock_whisper_model.return_value
    mock_segment = mock.MagicMock()
    mock_segment.text = "Hello world"
    mock_model_instance.transcribe.return_value = ([mock_segment], mock.MagicMock())

    settings = get_settings()

    provider = FasterWhisperProvider(
        model_name="tiny.en",
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
