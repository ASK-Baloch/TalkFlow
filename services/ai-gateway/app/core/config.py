from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalkFlow AI Gateway"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str
    redis_url: str
    vad_enabled: bool = False
    vad_provider: str = "silero"
    vad_device: str = "cpu"
    vad_use_onnx: bool = True

    vad_sample_rate: int = 8000
    vad_chunk_samples: int = 256

    vad_threshold: float = 0.50
    vad_neg_threshold: float = 0.35

    vad_min_speech_ms: int = 96
    vad_min_silence_ms: int = 256

    vad_max_speech_seconds: int = 30

    vad_pool_size: int = 4
    vad_pool_acquire_timeout_ms: int = 250

    vad_log_probabilities: bool = False

    ai_gateway_host: str = "0.0.0.0"
    ai_gateway_port: int = 8000

    audiosocket_host: str = "0.0.0.0"
    audiosocket_port: int = 9019

    audiosocket_echo_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
