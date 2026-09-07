from app.realtime.providers.loader import (
    create_provider,
)
from app.realtime.providers.stt_dummy import (
    DummySTTProvider,
)
from app.realtime.providers.tts_dummy import (
    DummyTTSProvider,
)


class Settings:
    stt_dummy_text = "hello"

    tts_sample_rate = 8000
    tts_frame_ms = 20
    tts_dummy_frames = 3


def test_dynamic_stt_loading():
    provider = create_provider(
        ("app.realtime.providers.stt_dummy:DummySTTProvider"),
        settings=Settings(),
    )

    assert isinstance(
        provider,
        DummySTTProvider,
    )


def test_dynamic_tts_loading():
    provider = create_provider(
        ("app.realtime.providers.tts_dummy:DummyTTSProvider"),
        settings=Settings(),
    )

    assert isinstance(
        provider,
        DummyTTSProvider,
    )
