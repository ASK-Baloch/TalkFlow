from functools import lru_cache

from pydantic import model_validator
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

    asr_enabled: bool = False
    asr_provider: str = "nemo"

    asr_model: str = "models/parakeet-unified-en-0.6b.nemo"
    asr_device: str = "cuda"
    asr_compute_type: str = "float16"

    asr_language: str = "en"

    asr_input_sample_rate: int = 8000
    asr_sample_rate: int = 16000

    asr_pre_roll_ms: int = 320

    asr_partial_enabled: bool = True
    asr_partial_min_audio_ms: int = 640
    asr_partial_interval_ms: int = 480

    asr_final_beam_size: int = 1
    asr_partial_beam_size: int = 1

    asr_max_utterance_seconds: int = 30

    asr_queue_maxsize: int = 16
    asr_workers: int = 1

    asr_log_partials: bool = True

    asr_word_timestamps: bool = False
    asr_condition_on_previous_text: bool = False
    asr_initial_prompt: str = "TalkFlow."
    qualification_enabled: bool = False
    qualification_min_age: int = 65
    qualification_zip_length: int = 5
    qualification_max_clarifications_per_field: int = 3
    qualification_log_state_transitions: bool = True
    qualification_log_field_values: bool = False
    qualification_debug_endpoints: bool = False
    audiosocket_echo_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        if self.qualification_min_age < 0:
            raise ValueError("QUALIFICATION_MIN_AGE must be >= 0")

        if self.qualification_zip_length != 5:
            raise ValueError("Phase 4 currently expects 5-digit ZIP codes")

        if self.qualification_max_clarifications_per_field < 1:
            raise ValueError("QUALIFICATION_MAX_CLARIFICATIONS_PER_FIELD must be >= 1")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_asr_vocabulary() -> dict:
    from pathlib import Path

    import yaml

    vocab_path = (
        Path(__file__).parent.parent.parent.parent.parent
        / "config"
        / "asr_domain_terms.yaml"
    )
    if not vocab_path.exists():
        return {"terms": {}, "global": [], "states": {}}

    with open(vocab_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"terms": {}, "global": [], "states": {}}
