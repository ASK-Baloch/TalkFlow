import asyncio
import json
import math
import struct
import uuid

import httpx


async def send_audio(writer, freq=1000, duration_sec=1.0, sample_rate=8000):
    num_samples = int(sample_rate * duration_sec)
    for i in range(0, num_samples, 320):  # chunks of 320 samples
        chunk_samples = min(320, num_samples - i)
        pcm = bytearray()
        for j in range(chunk_samples):
            t = (i + j) / sample_rate
            val = int(32767.0 * math.sin(2.0 * math.pi * freq * t))
            pcm.extend(struct.pack("<h", val))

        # AudioSocket 16-bit SLIN payload (type 0x10)
        # payload_length = len(pcm)
        header = struct.pack("!B H", 0x10, len(pcm))
        writer.write(header + pcm)
        await writer.drain()
        await asyncio.sleep(chunk_samples / sample_rate)


async def run():
    connection_id = str(uuid.uuid4())

    # 1. Fetch initial status
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8000/internal/tts/status")
        resp.raise_for_status()
        initial_status = resp.json()
        print("Initial status:", json.dumps(initial_status, indent=2))

        # 2. Open AudioSocket TCP connection
        _reader, writer = await asyncio.open_connection("localhost", 9019)

        # Send ID payload (type 0x01)
        id_bytes = uuid.UUID(connection_id).bytes
        header = struct.pack("!B H", 0x01, len(id_bytes))
        writer.write(header + id_bytes)
        await writer.drain()

        # Wait a moment to establish session and for log to flush
        await asyncio.sleep(1.0)

        # Find connection_id from docker logs
        proc = await asyncio.create_subprocess_shell(
            "docker compose logs --tail 200 ai-gateway", stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        log_out = stdout.decode()

        real_connection_id = None
        import re

        m = re.search(r"connection_id=([\w-]+) uuid=" + connection_id, log_out)
        if m:
            real_connection_id = m.group(1)

        if not real_connection_id:
            raise RuntimeError(
                f"Could not find connection_id for uuid {connection_id} in logs"
            )

        print(f"Found real connection_id: {real_connection_id}")

        # 3. Trigger Dynamic TTS (5 seconds dummy)
        print("Triggering dynamic TTS playback...")
        resp = await client.post(
            "http://localhost:8000/internal/tts/dynamic",
            json={
                "connection_id": real_connection_id,
                "text": "Simulating a long dummy text for barge-in test.",
            },
        )
        resp.raise_for_status()

        # Wait slightly so playback actually begins
        await asyncio.sleep(0.5)

        # 4. Check active_playbacks == 1
        resp = await client.get("http://localhost:8000/internal/tts/status")
        status = resp.json()
        print(f"Active playbacks after start: {status['active_playbacks']}")
        assert status["active_playbacks"] >= 1, "Playback did not start properly"

        # 5. Send loud sine wave to trigger VAD SPEECH_START
        print("Sending audio to trigger SPEECH_START...")
        await send_audio(writer, duration_sec=1.0)

        # 6. Wait for cancellation to propagate
        await asyncio.sleep(1.0)

        # 7. Fetch final status and verify
        resp = await client.get("http://localhost:8000/internal/tts/status")
        final_status = resp.json()
        print("Final status:", json.dumps(final_status, indent=2))

        assert final_status["active_playbacks"] == 0, (
            "Playback is still active, it didn't cancel"
        )
        assert (
            final_status["interruptions_total"] > initial_status["interruptions_total"]
        ), "interruptions_total didn't increment"
        assert (
            final_status["interrupted_playbacks_total"]
            > initial_status["interrupted_playbacks_total"]
        ), "interrupted_playbacks_total didn't increment"
        print("\nSUCCESS! Barge-in integration test fully passed.")

        # Cleanup
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(run())
