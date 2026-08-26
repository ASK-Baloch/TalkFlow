import asyncio
from dataclasses import dataclass

from .constants import HEADER_SIZE, MAX_PAYLOAD_SIZE


@dataclass(slots=True)
class AudioSocketPacket:
    message_type: int
    payload: bytes


class AudioSocketProtocolError(Exception):
    pass


async def read_packet(
    reader: asyncio.StreamReader,
) -> AudioSocketPacket:
    header = await reader.readexactly(HEADER_SIZE)

    message_type = header[0]
    payload_length = int.from_bytes(
        header[1:3],
        byteorder="big",
        signed=False,
    )

    if payload_length > MAX_PAYLOAD_SIZE:
        raise AudioSocketProtocolError(
            f"Invalid payload length: {payload_length}"
        )

    if payload_length == 0:
        payload = b""
    else:
        payload = await reader.readexactly(payload_length)

    return AudioSocketPacket(
        message_type=message_type,
        payload=payload,
    )


def encode_packet(
    message_type: int,
    payload: bytes = b"",
) -> bytes:
    payload_length = len(payload)

    if payload_length > MAX_PAYLOAD_SIZE:
        raise AudioSocketProtocolError(
            f"Payload too large: {payload_length}"
        )

    header = bytes([message_type]) + payload_length.to_bytes(
        2,
        byteorder="big",
        signed=False,
    )

    return header + payload


async def write_packet(
    writer: asyncio.StreamWriter,
    message_type: int,
    payload: bytes = b"",
) -> None:
    writer.write(
        encode_packet(
            message_type=message_type,
            payload=payload,
        )
    )

    await writer.drain()