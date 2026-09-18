from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalkFlow Auth Service"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://talkflow:admin@localhost:5432/talkflow"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    token_blacklist_ttl: int = 3600
    role_cache_ttl: int = 300

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    seed_admin_email: str = "admin@phonova.io"
    seed_admin_password: str = "admin123"
    seed_admin_full_name: str = "Admin MPN"

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
