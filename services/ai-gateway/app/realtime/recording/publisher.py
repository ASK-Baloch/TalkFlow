import json
import logging

from aiokafka import AIOKafkaProducer

logger = logging.getLogger("talkflow.recording")


class RecordingRequestPublisher:
    def __init__(
        self, bootstrap_servers: str, topic: str = "talkflow.recording.requests.v1"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if self.producer is not None:
            return

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()
        logger.info("RecordingRequestPublisher started.")

    async def stop(self) -> None:
        if self.producer is None:
            return

        await self.producer.stop()
        self.producer = None
        logger.info("RecordingRequestPublisher stopped.")

    async def publish_call_ended(self, call_id: str) -> None:
        if self.producer is None:
            logger.warning(
                "RecordingRequestPublisher not started, dropping event for call %s",
                call_id,
            )
            return

        from datetime import datetime, timezone

        payload = {
            "event": "call_ended",
            "call_id": call_id,
            "ended_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        try:
            await self.producer.send_and_wait(self.topic, payload)
            logger.info("Published call_ended event for call %s", call_id)
        except Exception:
            logger.exception("Failed to publish call_ended event for call %s", call_id)
