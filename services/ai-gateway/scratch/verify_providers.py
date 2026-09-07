from app.core.config import Settings
from app.realtime.providers.loader import create_provider


def verify_providers():
    settings = Settings()

    providers = [
        "app.realtime.providers.stt_faster_whisper:FasterWhisperSTTProvider",
        "app.realtime.providers.stt_dummy:DummySTTProvider",
        "app.realtime.providers.tts_chatterbox_http:ChatterboxHttpTTSProvider",
        "app.realtime.providers.tts_dummy:DummyTTSProvider",
        "app.realtime.providers.tts_pregenerated:PregeneratedTTSProvider",
    ]

    for p in providers:
        print(f"Loading {p}...")
        try:
            instance = create_provider(p, settings=settings)
            print(f"SUCCESS: {instance.__class__.__name__}")
        except Exception as e:
            print(f"FAILED: {p} - {e}")
            raise


if __name__ == "__main__":
    verify_providers()
