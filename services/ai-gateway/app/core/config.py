from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalkFlow AI Gateway"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str
    redis_url: str
    vad_enabled: bool = True
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

    asr_enabled: bool = True
    asr_provider: str = "nemo"

    stt_provider_class: str = (
        "app.realtime.providers.stt_faster_whisper:FasterWhisperSTTProvider"
    )

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

    asr_final_beam_size: int = 5
    asr_partial_beam_size: int = 1

    asr_max_utterance_seconds: int = 30

    asr_queue_maxsize: int = 16
    asr_workers: int = 1

    asr_log_partials: bool = True

    asr_word_timestamps: bool = False
    asr_condition_on_previous_text: bool = False
    asr_initial_prompt: str = "TalkFlow."
    qualification_enabled: bool = True
    qualification_min_age: int = 65
    qualification_zip_length: int = 5
    qualification_max_clarifications_per_field: int = 3
    qualification_log_state_transitions: bool = True
    qualification_log_field_values: bool = False
    qualification_debug_endpoints: bool = False
    audiosocket_echo_enabled: bool = False
    tts_enabled: bool = True

    tts_pregenerated_provider_class: str = (
        "app.realtime.providers.tts_pregenerated:PregeneratedTTSProvider"
    )
    tts_dynamic_provider_class: str = (
        "app.realtime.providers.tts_chatterbox_http:ChatterboxHttpTTSProvider"
    )
    tts_worker_url: str = "http://127.0.0.1:8091"
    tts_worker_timeout_seconds: float = 5.0
    tts_default_voice_id: str = "talkflow_primary"

    tts_mode: str = "pregenerated"

    tts_asset_version: str = "talkflow-v1"
    tts_asset_dir: str = "assets/tts/talkflow-v1"

    tts_sample_rate: int = 8000
    tts_sample_width_bytes: int = 2
    tts_channels: int = 1

    tts_frame_ms: int = 20

    tts_cache_enabled: bool = True
    tts_cache_prefix: str = "talkflow:tts"
    tts_cache_local_fallback: bool = True

    tts_redis_db: int = 0

    tts_playback_queue_size: int = 8
    tts_interrupt_enabled: bool = True

    barge_in_enabled: bool = True
    barge_in_min_speech_ms: int = 96
    barge_in_cancel_current_playback: bool = True
    barge_in_flush_playback_queue: bool = True
    barge_in_drop_stale_audio: bool = True
    barge_in_grace_ms: int = 0
    barge_in_log_events: bool = True

    tts_voice: str = "af_heart"
    tts_speed: float = 1.0
    tts_language: str = "en-us"

    tts_log_text: bool = False

    tts_dummy_frames: int = 10
    stt_dummy_text: str = "Yes"

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        case_sensitive=False,
        extra="ignore",
    )

    llm_enabled: bool = True
    llm_provider_class: str = (
        "app.realtime.providers.llm_openai_compat:OpenAICompatibleLLMProvider"
    )
    llm_base_url: str = "http://vllm:8100/v1"
    llm_api_key: str = "EMPTY"
    llm_model: str = "Qwen/Qwen2.5-1.5B-Instruct-AWQ"
    llm_enable_thinking: bool = False
    llm_max_tokens: int = 80
    llm_temperature: float = 0.7
    llm_top_p: float = 0.8
    llm_top_k: int = 20
    llm_presence_penalty: float = 0.3
    llm_timeout_seconds: float = 5.0
    llm_max_history_turns: int = 4
    llm_max_input_chars: int = 2000
    llm_fallback_only: bool = True
    llm_dummy_response: str = (
        "I can help with that. Let's continue with the qualification questions."
    )
    llm_debug_endpoints: bool = True

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
