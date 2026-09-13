from __future__ import annotations

from pydantic import (
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database_url: str

    # asyncpg does not understand postgresql+asyncpg://
    @field_validator("database_url", mode="before")
    @classmethod
    def _strip_asyncpg(cls, v: str) -> str:
        return v.replace("+asyncpg://", "://")

    kafka_bootstrap_servers: str = "kafka:9092"

    recording_request_topic: str = "talkflow.recording.requests.v1"

    recording_ready_topic: str = "talkflow.recording.ready.v1"

    recording_failed_topic: str = "talkflow.recording.failed.v1"

    recording_asterisk_dir: str = "/var/spool/asterisk/monitor/talkflow"

    recording_format: str = "wav"

    recording_finalize_delay_seconds: float = 2.0

    recording_stable_check_interval_seconds: float = 1.0

    recording_stable_checks_required: int = 2

    recording_max_wait_seconds: float = 60.0

    recording_max_file_bytes: int = 1_073_741_824

    recording_default_retention_days: int = 90

    recording_storage_provider: str = "local"

    recording_local_storage_dir: str = "/app/storage/recordings"

    recording_delete_source_after_ready: bool = False

    asterisk_sftp_host: str

    asterisk_sftp_port: int = 22

    asterisk_sftp_username: str

    asterisk_sftp_private_key: str

    asterisk_sftp_known_hosts: str

    asterisk_sftp_passphrase: str | None = None

    recording_s3_endpoint: str | None = None

    recording_s3_region: str | None = None

    recording_s3_bucket: str | None = None

    recording_s3_access_key_id: str | None = None

    recording_s3_secret_access_key: str | None = None


settings = Settings()
