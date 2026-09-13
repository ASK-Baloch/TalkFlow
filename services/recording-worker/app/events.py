from __future__ import annotations

import json
from datetime import (
    datetime,
    timezone,
)

from aiokafka import (
    AIOKafkaProducer,
)

from app.config import Settings
from app.types import (
    RecordingFileInfo,
    StoredRecording,
)


class RecordingEventPublisher:
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self.settings = settings

        self.producer = AIOKafkaProducer(
            bootstrap_servers=(settings.kafka_bootstrap_servers)
        )

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def ready(
        self,
        *,
        call_id: str,
        file_info: RecordingFileInfo,
        stored: StoredRecording,
    ) -> None:
        payload = {
            "schema_version": 1,
            "event_type": ("recording.ready"),
            "call_id": call_id,
            "storage_provider": (stored.provider),
            "storage_key": (stored.storage_key),
            "size_bytes": (file_info.size_bytes),
            "duration_ms": (file_info.duration_ms),
            "sample_rate": (file_info.sample_rate),
            "channels": (file_info.channels),
            "sha256": (file_info.sha256),
            "available_at": (datetime.now(timezone.utc).isoformat()),
        }

        await self.producer.send_and_wait(
            self.settings.recording_ready_topic,
            json.dumps(payload).encode("utf-8"),
            key=call_id.encode("utf-8"),
        )

    async def failed(
        self,
        *,
        call_id: str,
        error: str,
    ) -> None:
        payload = {
            "schema_version": 1,
            "event_type": ("recording.failed"),
            "call_id": call_id,
            "error": error[:2000],
            "failed_at": (datetime.now(timezone.utc).isoformat()),
        }

        await self.producer.send_and_wait(
            self.settings.recording_failed_topic,
            json.dumps(payload).encode("utf-8"),
            key=call_id.encode("utf-8"),
        )
