from __future__ import annotations

import asyncio
from time import perf_counter

PCM_8K_MESSAGE_TYPE = 0x10


def encode_audiosocket_packet(
    *,
    message_type: int,
    payload: bytes,
) -> bytes:
    if len(payload) > 0xFFFF:
        raise ValueError(
            "AudioSocket payload too large"
        )

    return bytes(
        [
            message_type,
            (len(payload) >> 8)
            & 0xFF,
            len(payload) & 0xFF,
        ]
    ) + payload


class AudioSocketPcmPlayer:
    def __init__(
        self,
        *,
        sample_rate: int = 8000,
        sample_width_bytes: int = 2,
        frame_ms: int = 20,
    ) -> None:
        self.sample_rate = sample_rate

        self.sample_width_bytes = (
            sample_width_bytes
        )

        self.frame_ms = frame_ms

        self.samples_per_frame = int(
            self.sample_rate
            * self.frame_ms
            / 1000
        )

        self.bytes_per_frame = (
            self.samples_per_frame
            * self.sample_width_bytes
        )

    async def play(
        self,
        *,
        writer: asyncio.StreamWriter,
        pcm: bytes,
    ) -> None:
        if len(pcm) % (
            self.sample_width_bytes
        ):
            raise ValueError(
                "PCM payload has invalid byte length"
            )

        frame_duration = (
            self.frame_ms / 1000.0
        )

        loop = asyncio.get_running_loop()

        next_deadline = (
            loop.time()
        )

        offset = 0

        while offset < len(pcm):
            payload = pcm[
                offset:
                offset
                + self.bytes_per_frame
            ]

            if (
                len(payload)
                < self.bytes_per_frame
            ):
                payload += bytes(
                    self.bytes_per_frame
                    - len(payload)
                )

            packet = (
                encode_audiosocket_packet(
                    message_type=(
                        PCM_8K_MESSAGE_TYPE
                    ),
                    payload=payload,
                )
            )

            writer.write(
                packet
            )

            await writer.drain()

            offset += (
                self.bytes_per_frame
            )

            next_deadline += (
                frame_duration
            )

            delay = (
                next_deadline
                - loop.time()
            )

            if delay > 0:
                await asyncio.sleep(
                    delay
                )