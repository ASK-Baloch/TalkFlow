import asyncio
import json
import os
import uuid
from datetime import datetime

import asyncssh
from aiokafka import AIOKafkaProducer


async def main():
    fake_uuid = str(uuid.uuid4())
    print(f"Testing UUID: {fake_uuid}")

    # 1. Create a corrupt WAV file on the remote Asterisk server
    print("Connecting to SFTP...")
    async with (
        asyncssh.connect(
            host="136.243.116.238",
            port=22,
            username="talkflow_recordings",
            client_keys=["/run/secrets/asterisk_recording_key"],
            known_hosts="/run/secrets/asterisk_known_hosts",
            passphrase="ssh",
        ) as conn,
        conn.start_sftp_client() as sftp,
    ):
        remote_path = f"/var/spool/asterisk/monitor/talkflow/{fake_uuid}.wav"
        print(f"Writing corrupt file to {remote_path}")
        async with sftp.open(remote_path, "wb") as f:
            await f.write(os.urandom(1024 * 10))  # 10 KB of random bytes

        # Wait for file to become "stable" by giving it a second
        await asyncio.sleep(2)

    # 2. Publish Kafka event
    print("Publishing Kafka event...")
    p = AIOKafkaProducer(bootstrap_servers="kafka:9092")
    await p.start()
    msg = json.dumps(
        {"call_id": fake_uuid, "ended_at": datetime.utcnow().isoformat() + "Z"}
    ).encode()
    await p.send_and_wait("talkflow.recording.requests.v1", msg)
    await p.stop()

    print(f"Fake UUID {fake_uuid} published. Worker will now process it.")


if __name__ == "__main__":
    asyncio.run(main())
