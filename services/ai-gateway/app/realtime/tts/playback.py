from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

PCM_8K_MESSAGE_TYPE = 0x10


def encode_audiosocket_packet(
    *,
    message_type: int,
    payload: bytes,
) -> bytes:
    if len(payload) > 0xFFFF:
        raise ValueError("AudioSocket payload too large")

    return (
        bytes(
            [
                message_type,
                (len(payload) >> 8) & 0xFF,
                len(payload) & 0xFF,
            ]
        )
        + payload
    )


class PlaybackInterrupted(Exception):
    pass


class AudioSocketPcmPlayer:
    def __init__(
        self,
        *,
        sample_rate: int = 8000,
        sample_width_bytes: int = 2,
        frame_ms: int = 20,
    ) -> None:
        self.sample_rate = sample_rate

        self.sample_width_bytes = sample_width_bytes

        self.frame_ms = frame_ms

        self.samples_per_frame = int(self.sample_rate * self.frame_ms / 1000)

        self.bytes_per_frame = self.samples_per_frame * self.sample_width_bytes

    async def play_chunks(
        self,
        *,
        writer: asyncio.StreamWriter,
        chunks,
        should_continue: Callable[
            [],
            Awaitable[bool],
        ],
        on_first_frame: Callable[
            [],
            Awaitable[None],
        ]
        | None = None,
    ) -> None:
        loop = asyncio.get_running_loop()

        frame_duration = self.frame_ms / 1000.0

        next_deadline = loop.time()

        first_frame_sent = False

        buffer = bytearray()

        async for chunk in chunks:
            if not await should_continue():
                raise PlaybackInterrupted

            if not chunk.pcm:
                continue

            buffer.extend(chunk.pcm)

            while len(buffer) >= (self.bytes_per_frame):
                if not await should_continue():
                    raise PlaybackInterrupted

                payload = bytes(buffer[: self.bytes_per_frame])

                del buffer[: self.bytes_per_frame]

                packet = encode_audiosocket_packet(
                    message_type=(PCM_8K_MESSAGE_TYPE),
                    payload=payload,
                )

                writer.write(packet)

                await writer.drain()

                if not first_frame_sent:
                    first_frame_sent = True

                    if on_first_frame:
                        await on_first_frame()

                next_deadline += frame_duration

                delay = next_deadline - loop.time()

                if delay > 0:
                    await asyncio.sleep(delay)

        if buffer:
            if not await should_continue():
                raise PlaybackInterrupted

            if len(buffer) < (self.bytes_per_frame):
                buffer.extend(bytes(self.bytes_per_frame - len(buffer)))

            packet = encode_audiosocket_packet(
                message_type=(PCM_8K_MESSAGE_TYPE),
                payload=bytes(buffer),
            )

            writer.write(packet)

            await writer.drain()

            if not first_frame_sent and on_first_frame:
                await on_first_frame()
