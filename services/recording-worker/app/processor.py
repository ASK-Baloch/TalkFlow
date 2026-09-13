from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from app.config import Settings
from app.events import (
    RecordingEventPublisher,
)
from app.repository import (
    RecordingRepository,
)
from app.source import (
    AsteriskRecordingSource,
)
from app.storage.base import (
    RecordingStorageProvider,
)
from app.types import (
    RecordingRequest,
)
from app.validator import (
    validate_wav,
)


class RecordingProcessor:
    def __init__(
        self,
        *,
        settings: Settings,
        source: AsteriskRecordingSource,
        storage: (RecordingStorageProvider),
        repository: (RecordingRepository),
        events: (RecordingEventPublisher),
    ) -> None:
        self.settings = settings

        self.source = source

        self.storage = storage

        self.repository = repository

        self.events = events

    async def process(
        self,
        request: RecordingRequest,
    ) -> None:
        remote_path = self.source.remote_path(request.call_id)

        await self.repository.ensure_pending(
            call_id=(request.call_id),
            source_path=(remote_path),
            ended_at=(request.ended_at),
        )

        try:
            await asyncio.sleep(self.settings.recording_finalize_delay_seconds)

            await self.repository.set_status(
                call_id=(request.call_id),
                status=("WAITING_FOR_SOURCE"),
            )

            remote_path = await self.source.wait_until_stable(call_id=(request.call_id))

            await self.repository.set_status(
                call_id=(request.call_id),
                status="FETCHING",
            )

            with tempfile.TemporaryDirectory(
                prefix=("talkflow-recording-")
            ) as temporary:
                local_path = Path(temporary) / (request.call_id + ".wav")

                await self.source.fetch(
                    remote_path=(remote_path),
                    destination=(local_path),
                )

                await self.repository.set_status(
                    call_id=(request.call_id),
                    status=("VALIDATING"),
                )

                file_info = validate_wav(
                    local_path,
                    max_file_bytes=(self.settings.recording_max_file_bytes),
                )

                await self.repository.set_status(
                    call_id=(request.call_id),
                    status="STORING",
                )

                stored = await self.storage.store(
                    call_id=(request.call_id),
                    source=(local_path),
                )

                await self.repository.mark_ready(
                    call_id=(request.call_id),
                    storage_provider=(stored.provider),
                    storage_key=(stored.storage_key),
                    size_bytes=(file_info.size_bytes),
                    duration_ms=(file_info.duration_ms),
                    sample_rate=(file_info.sample_rate),
                    channels=(file_info.channels),
                    sha256=(file_info.sha256),
                )

                await self.events.ready(
                    call_id=(request.call_id),
                    file_info=(file_info),
                    stored=stored,
                )

        except Exception as exc:
            await self.repository.mark_failed(
                call_id=(request.call_id),
                error_code=("PROCESSING_FAILED"),
                error_message=(str(exc)),
            )

            await self.events.failed(
                call_id=(request.call_id),
                error=str(exc),
            )

            raise
