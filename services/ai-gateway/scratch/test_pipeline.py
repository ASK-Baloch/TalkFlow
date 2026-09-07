import asyncio
import struct
import uuid


async def test_pipeline():
    reader, writer = await asyncio.open_connection("127.0.0.1", 9019)
    session_uuid = uuid.uuid4()

    # 0x01: Client Setup (16-byte UUID)
    header = struct.pack(">BH", 0x01, 16)
    writer.write(header + session_uuid.bytes)

    # Send ~1s of silent audio (8kHz, 16-bit PCM = 16000 bytes)
    audio = b"\x00\x00" * 8000

    # Split into 320 byte chunks (20ms)
    for i in range(0, len(audio), 320):
        chunk = audio[i : i + 320]
        header = struct.pack(">BH", 0x10, len(chunk))
        writer.write(header + chunk)
        await asyncio.sleep(0.01)  # stream it

    await writer.drain()

    print(f"Sent 1s of audio on connection {session_uuid}")

    while True:
        try:
            # Read header
            header_bytes = await reader.readexactly(3)
            msg_type, payload_len = struct.unpack(">BH", header_bytes)

            if payload_len > 0:
                _ = await reader.readexactly(payload_len)
            else:
                pass

            print(f"Received msg_type=0x{msg_type:02x}, len={payload_len}")

            if msg_type == 0x00:  # End of stream
                break
        except asyncio.exceptions.IncompleteReadError:
            break

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(test_pipeline())
