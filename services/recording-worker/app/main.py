from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime

from aiokafka import (
    AIOKafkaConsumer,
)

from app.call_id import (
    validate_call_id,
)
from app.config import (
    settings,
)
from app.events import (
    RecordingEventPublisher,
)
from app.processor import (
    RecordingProcessor,
)
from app.repository import (
    RecordingRepository,
)
from app.source import (
    AsteriskRecordingSource,
)
from app.storage.factory import (
    create_storage,
)
from app.types import (
    RecordingRequest,
)

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("talkflow.recording_worker")


async def main() -> None:
    repository = RecordingRepository(
        database_url=(settings.database_url),
        retention_days=(settings.recording_default_retention_days),
    )

    source = AsteriskRecordingSource(settings)

    storage = create_storage(settings)

    events = RecordingEventPublisher(settings)

    processor = RecordingProcessor(
        settings=settings,
        source=source,
        storage=storage,
        repository=repository,
        events=events,
    )

    consumer = AIOKafkaConsumer(
        settings.recording_request_topic,
        bootstrap_servers=(settings.kafka_bootstrap_servers),
        group_id=("talkflow-recording-workers-v1"),
        enable_auto_commit=False,
        auto_offset_reset=("earliest"),
    )

    await repository.start()

    await events.start()

    await consumer.start()

    logger.info("Recording worker started")

    try:
        async for message in consumer:
            try:
                payload = json.loads(message.value.decode("utf-8"))

                call_id = validate_call_id(payload["call_id"])

                from datetime import timezone

                ended_at_str = payload.get("ended_at")
                if ended_at_str:
                    ended_at = datetime.fromisoformat(
                        ended_at_str.replace("Z", "+00:00")
                    )
                else:
                    ended_at = datetime.now(timezone.utc)

                request = RecordingRequest(
                    call_id=(call_id),
                    ended_at=(ended_at),
                )

                await processor.process(request)

                await consumer.commit()

            except Exception:
                logger.exception("Recording job failed")

                # Do not commit the offset.
                # This allows later retry/recovery.

    finally:
        await consumer.stop()

        await events.stop()

        await repository.stop()


if __name__ == "__main__":
    asyncio.run(main())
