import asyncio

import pytest

from app.realtime.audiosocket.protocol import (
    encode_packet,
    read_packet,
)


def test_encode_pcm_packet():
    payload = b"\x01\x02\x03\x04"

    packet = encode_packet(
        message_type=0x10,
        payload=payload,
    )

    assert packet[0] == 0x10
    assert packet[1:3] == b"\x00\x04"
    assert packet[3:] == payload


@pytest.mark.asyncio
async def test_read_packet():
    payload = b"\x01\x02\x03\x04"

    data = (
        bytes([0x10])
        + len(payload).to_bytes(2, "big")
        + payload
    )

    reader = asyncio.StreamReader()
    reader.feed_data(data)
    reader.feed_eof()

    packet = await read_packet(reader)

    assert packet.message_type == 0x10
    assert packet.payload == payload