import numpy as np

from app.realtime.providers.stt_dummy import (
    DummySTTProvider,
)


class Settings:
    stt_dummy_text = "My ZIP code is 75001."


def test_dummy_stt_provider():
    provider = DummySTTProvider.from_settings(Settings())

    audio = np.zeros(
        16000,
        dtype=np.float32,
    )

    result = provider.transcribe(audio)

    assert result.text == "My ZIP code is 75001."

    assert result.language == "en"
