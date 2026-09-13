from __future__ import annotations

import asyncio
from pathlib import Path

import boto3

from app.storage.base import (
    RecordingStorageProvider,
)
from app.types import (
    StoredRecording,
)


class S3RecordingStorage(RecordingStorageProvider):
    def __init__(
        self,
        *,
        endpoint_url: str | None,
        region_name: str | None,
        bucket: str,
        access_key_id: str,
        secret_access_key: str,
    ) -> None:
        self.bucket = bucket

        self.client = boto3.client(
            "s3",
            endpoint_url=(endpoint_url),
            region_name=(region_name),
            aws_access_key_id=(access_key_id),
            aws_secret_access_key=(secret_access_key),
        )

    async def store(
        self,
        *,
        call_id: str,
        source: Path,
    ) -> StoredRecording:
        key = f"recordings/{call_id[:2]}/{call_id}.wav"

        await asyncio.to_thread(
            self.client.upload_file,
            str(source),
            self.bucket,
            key,
            ExtraArgs={"ContentType": ("audio/wav")},
        )

        return StoredRecording(
            provider="s3",
            storage_key=key,
            size_bytes=(source.stat().st_size),
        )
