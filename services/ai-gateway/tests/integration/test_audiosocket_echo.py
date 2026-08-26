import asyncio
import uuid

import pytest

from app.realtime.audiosocket.protocol import (
    encode_packet,
    read_packet,
)
from app.realtime.audiosocket.server import AudioSocketServer


@pytest.mark.asyncio
async def test_echo_audio():
    server = AudioSocketServer()

    server.host = "127.0.0.1"
    server.port = 19019
    server.echo_enabled = True

    await server.start()

    try:
        reader, writer = await asyncio.open_connection(
            "127.0.0.1",
            19019,
        )

        session_uuid = uuid.uuid4()

        writer.write(
            encode_packet(
                0x01,
                session_uuid.bytes,
            )
        )

        payload = b"\x00\x01" * 160

        writer.write(
            encode_packet(
                0x10,
                payload,
            )
        )

        await writer.drain()

        response = await read_packet(reader)

        assert response.message_type == 0x10
        assert response.payload == payload

        writer.write(
            encode_packet(
                0x00,
            )
        )

        await writer.drain()

        writer.close()
        await writer.wait_closed()

    finally:
        await server.stop()