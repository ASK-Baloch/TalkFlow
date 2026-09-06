from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from time import perf_counter_ns

from app.core.config import (
    get_settings,
)
from app.realtime.qualification.types import (
    ConversationAction,
)

from .catalog import (
    response_for_action,
)
from .metrics import tts_metrics
from .playback import (
    AudioSocketPcmPlayer,
)
from .types import (
    PlaybackRequest,
)

logger = logging.getLogger(
    "talkflow.tts"
)


@dataclass
class PlaybackConnection:
    connection_id: str

    writer: asyncio.StreamWriter

    queue: asyncio.Queue[
        PlaybackRequest
    ]

    worker_task: asyncio.Task | None = (
        None
    )


class TTSService:
    def __init__(
        self,
        pregenerated_provider=None,
        dynamic_provider=None,
    ) -> None:
        settings = get_settings()

        self.settings = settings

        self.enabled = (
            settings.tts_enabled
        )

        self._connections: dict[
            str,
            PlaybackConnection,
        ] = {}

        self.pregenerated_provider = pregenerated_provider
        self.dynamic_provider = dynamic_provider

        self.player = (
            AudioSocketPcmPlayer(
                sample_rate=(
                    settings.tts_sample_rate
                ),
                sample_width_bytes=(
                    settings
                    .tts_sample_width_bytes
                ),
                frame_ms=(
                    settings.tts_frame_ms
                ),
            )
        )

    async def start(
        self,
    ) -> None:
        if not self.enabled:
            logger.info(
                "Pre-generated TTS disabled"
            )

            return

        if hasattr(self.pregenerated_provider, "start"):
            await self.pregenerated_provider.start()

        if hasattr(self.dynamic_provider, "start"):
            await self.dynamic_provider.start()

        logger.info(
            (
                "Pre-generated TTS ready "
                "version=%s "
                "sample_rate=%s"
            ),
            self.settings
            .tts_asset_version,
            self.settings
            .tts_sample_rate,
        )

    async def stop(
        self,
    ) -> None:
        connection_ids = list(
            self._connections
        )

        for connection_id in (
            connection_ids
        ):
            await self.detach_connection(
                connection_id
            )

        if hasattr(self.pregenerated_provider, "stop"):
            await self.pregenerated_provider.stop()

        if hasattr(self.dynamic_provider, "stop"):
            await self.dynamic_provider.stop()

    async def attach_connection(
        self,
        *,
        connection_id: str,
        writer: asyncio.StreamWriter,
    ) -> None:
        if not self.enabled:
            return

        if (
            connection_id
            in self._connections
        ):
            return

        queue: asyncio.Queue[
            PlaybackRequest
        ] = asyncio.Queue(
            maxsize=(
                self.settings
                .tts_playback_queue_size
            )
        )

        connection = (
            PlaybackConnection(
                connection_id=(
                    connection_id
                ),
                writer=writer,
                queue=queue,
            )
        )

        self._connections[
            connection_id
        ] = connection

        connection.worker_task = (
            asyncio.create_task(
                self._playback_worker(
                    connection
                )
            )
        )

        tts_metrics.playback_sessions_total += 1

        logger.info(
            (
                "TTS connection attached "
                "connection_id=%s"
            ),
            connection_id,
        )

    async def detach_connection(
        self,
        connection_id: str,
    ) -> None:
        connection = (
            self._connections.pop(
                connection_id,
                None,
            )
        )

        if connection is None:
            return

        if (
            connection.worker_task
            is not None
        ):
            connection.worker_task.cancel()

            await asyncio.gather(
                connection.worker_task,
                return_exceptions=True,
            )

        logger.info(
            (
                "TTS connection detached "
                "connection_id=%s"
            ),
            connection_id,
        )

    async def handle_action(
        self,
        *,
        connection_id: str,
        session_uuid: str | None,
        action: ConversationAction,
    ) -> bool:
        if not self.enabled:
            return False

        definition = (
            response_for_action(
                action.action_type
            )
        )

        if definition is None:
            return False

        connection = (
            self._connections.get(
                connection_id
            )
        )

        if connection is None:
            logger.warning(
                (
                    "No TTS playback connection "
                    "connection_id=%s"
                ),
                connection_id,
            )

            return False

        request = PlaybackRequest(
            connection_id=(
                connection_id
            ),
            session_uuid=(
                session_uuid
            ),
            response_id=(
                definition.response_id
            ),
        )

        if connection.queue.full():
            tts_metrics.queue_overflows += 1

            logger.error(
                (
                    "TTS playback queue full "
                    "connection_id=%s"
                ),
                connection_id,
            )

            return False

        connection.queue.put_nowait(
            request
        )

        tts_metrics.requests_total += 1

        return True

    async def play_initial_prompt(
        self,
        *,
        connection_id: str,
        session_uuid: str | None,
        action: ConversationAction,
    ) -> bool:
        return await self.handle_action(
            connection_id=(
                connection_id
            ),
            session_uuid=(
                session_uuid
            ),
            action=action,
        )

    async def play_text(
        self,
        *,
        connection_id: str,
        session_uuid: str | None,
        text: str,
    ) -> bool:
        if not self.enabled:
            return False

        connection = (
            self._connections.get(
                connection_id
            )
        )

        if connection is None:
            logger.warning(
                (
                    "No TTS playback connection "
                    "connection_id=%s"
                ),
                connection_id,
            )

            return False

        request = PlaybackRequest(
            connection_id=(
                connection_id
            ),
            session_uuid=(
                session_uuid
            ),
            text=text,
        )

        if connection.queue.full():
            tts_metrics.queue_overflows += 1

            logger.error(
                (
                    "TTS playback queue full "
                    "connection_id=%s"
                ),
                connection_id,
            )

            return False

        connection.queue.put_nowait(
            request
        )

        tts_metrics.requests_total += 1

        return True

    async def _playback_worker(
        self,
        connection: PlaybackConnection,
    ) -> None:
        while True:
            request = (
                await connection
                .queue.get()
            )

            try:
                started_ns = (
                    perf_counter_ns()
                )

                from app.realtime.providers.tts import TTSRequest

                is_pregenerated = request.response_id is not None
                provider = self.pregenerated_provider if is_pregenerated else self.dynamic_provider

                tts_request = TTSRequest(
                    text=request.text,
                    response_id=request.response_id.value if request.response_id else None,
                )

                first_chunk = True
                total_duration_ms = 0.0

                self.player.reset()

                async for chunk in provider.stream(tts_request):
                    if first_chunk:
                        first_chunk = False
                        cache_ready_ns = perf_counter_ns()
                        first_audio_ms = (cache_ready_ns - request.created_ns) / 1_000_000.0
                        tts_metrics.first_audio_ms.append(first_audio_ms)
                        tts_metrics.active_playbacks += 1

                        logger.info(
                            (
                                "TTS playback start "
                                "connection_id=%s "
                                "type=%s "
                                "ready_ms=%.2f"
                            ),
                            connection.connection_id,
                            "pregenerated" if is_pregenerated else "dynamic",
                            first_audio_ms,
                        )

                    chunk_duration_ms = (len(chunk.pcm) / (chunk.sample_width_bytes * chunk.channels * chunk.sample_rate)) * 1000
                    total_duration_ms += chunk_duration_ms

                    await self.player.play_chunk(
                        writer=connection.writer,
                        pcm=chunk.pcm,
                    )

                tts_metrics.completed_total += 1

                total_ms = (
                    perf_counter_ns()
                    - started_ns
                ) / 1_000_000.0

                logger.info(
                    (
                        "TTS playback complete "
                        "connection_id=%s "
                        "type=%s "
                        "audio_duration_ms=%.1f "
                        "total_ms=%.1f"
                    ),
                    connection.connection_id,
                    "pregenerated" if is_pregenerated else "dynamic",
                    total_duration_ms,
                    total_ms,
                )

            except asyncio.CancelledError:
                raise

            except FileNotFoundError:
                tts_metrics.assets_missing += 1

                logger.exception(
                    "TTS asset missing"
                )

            except Exception:
                tts_metrics.playback_errors += 1

                logger.exception(
                    (
                        "TTS playback failure "
                        "connection_id=%s"
                    ),
                    connection.connection_id,
                )

            finally:
                tts_metrics.active_playbacks = max(
                    0,
                    tts_metrics.active_playbacks
                    - 1,
                )

                connection.queue.task_done()


    @property
    def connected_calls(
        self,
    ) -> int:
        return len(self._connections)

