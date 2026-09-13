import asyncio
import json
import uuid
from datetime import datetime

from aiokafka import AIOKafkaProducer


async def main():
    p = AIOKafkaProducer(bootstrap_servers="kafka:9092")
    await p.start()

    fake_uuid = str(uuid.uuid4())
    print(f"Publishing fake UUID: {fake_uuid}")

    msg = json.dumps(
        {"call_id": fake_uuid, "ended_at": datetime.utcnow().isoformat() + "Z"}
    ).encode()
    await p.send_and_wait("talkflow.recording.requests.v1", msg)

    await p.stop()


if __name__ == "__main__":
    asyncio.run(main())
