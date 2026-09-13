from __future__ import annotations

from app.config import Settings
from app.storage.base import (
    RecordingStorageProvider,
)
from app.storage.local import (
    LocalRecordingStorage,
)
from app.storage.s3 import (
    S3RecordingStorage,
)


def create_storage(
    settings: Settings,
) -> RecordingStorageProvider:
    provider = settings.recording_storage_provider.strip().lower()

    if provider == "local":
        return LocalRecordingStorage(root=(settings.recording_local_storage_dir))

    if provider == "s3":
        if not (
            settings.recording_s3_bucket
            and settings.recording_s3_access_key_id
            and settings.recording_s3_secret_access_key
        ):
            raise ValueError("Missing required S3 recording configuration")

        return S3RecordingStorage(
            endpoint_url=(settings.recording_s3_endpoint),
            region_name=(settings.recording_s3_region),
            bucket=(settings.recording_s3_bucket),
            access_key_id=(settings.recording_s3_access_key_id),
            secret_access_key=(settings.recording_s3_secret_access_key),
        )

    raise ValueError(f"Unsupported recording storage provider: {provider}")
