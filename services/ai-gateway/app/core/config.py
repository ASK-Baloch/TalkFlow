from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalkFlow AI Gateway"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str

    redis_url: str

    ai_gateway_host: str = "0.0.0.0"
    ai_gateway_port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
