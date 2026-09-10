import asyncio
import uuid
import wave

from app.realtime.audiosocket.protocol import encode_packet, read_packet


async def live_client(wav_path):
    print("Connecting to AI Gateway AudioSocket (127.0.0.1:9019)...")
    reader, writer = await asyncio.open_connection("127.0.0.1", 9019)

    session_id = uuid.uuid4()
    print(f"Starting session {session_id}")
    writer.write(encode_packet(0x01, session_id.bytes))
    await writer.drain()

    # Stream audio
    print(f"Streaming {wav_path} to gateway...")
    with wave.open(wav_path, "rb") as wf:
        while True:
            # 320 bytes = 160 frames (16kHz, 16bit mono) -> 10ms
            chunk = wf.readframes(160)
            if not chunk:
                break
            writer.write(encode_packet(0x10, chunk))
            await writer.drain()
            await asyncio.sleep(0.01)

    print("Finished sending audio. Waiting for TTS response chunks...")

    tts_chunks_received = 0
    total_tts_bytes = 0

    # Read the response
    while True:
        try:
            # Use a timeout to avoid hanging forever
            packet = await asyncio.wait_for(read_packet(reader), timeout=5.0)
            if packet.message_type == 0x10:
                tts_chunks_received += 1
                total_tts_bytes += len(packet.payload)
                print(
                    f"Received TTS packet {tts_chunks_received} (size {len(packet.payload)} bytes)"
                )
            elif packet.message_type == 0x00:
                print("Received END packet from server")
                break
        except asyncio.TimeoutError:
            print("Timeout waiting for more TTS packets.")
            break
        except Exception as e:
            print(f"Connection closed: {e}")
            break

    print(f"Total TTS bytes received: {total_tts_bytes}")

    writer.close()
    await writer.wait_closed()
    print("Test complete.")


if __name__ == "__main__":
    asyncio.run(live_client("scripts/test_set/001.wav"))
