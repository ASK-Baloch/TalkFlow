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

from .cache import TtsAssetCache
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


class PregeneratedTtsService:
    def __init__(
        self,
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

        self.cache = TtsAssetCache(
            prefix=(
                settings.tts_cache_prefix
            ),
            version=(
                settings.tts_asset_version
            ),
            asset_dir=(
                settings.tts_asset_dir
            ),
            cache_enabled=(
                settings.tts_cache_enabled
            ),
            local_fallback=(
                settings
                .tts_cache_local_fallback
            ),
        )

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

        await self.cache.start()

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

        await self.cache.stop()

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

                asset = (
                    await self.cache.get(
                        request.response_id
                    )
                )

                cache_ready_ns = (
                    perf_counter_ns()
                )

                first_audio_ms = (
                    cache_ready_ns
                    - request.created_ns
                ) / 1_000_000.0

                tts_metrics.first_audio_ms.append(
                    first_audio_ms
                )

                tts_metrics.active_playbacks += 1

                logger.info(
                    (
                        "TTS playback start "
                        "connection_id=%s "
                        "response_id=%s "
                        "duration_ms=%.1f "
                        "ready_ms=%.2f"
                    ),
                    connection.connection_id,
                    request.response_id.value,
                    asset.duration_ms,
                    first_audio_ms,
                )

                await self.player.play(
                    writer=(
                        connection.writer
                    ),
                    pcm=asset.pcm,
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
                        "response_id=%s "
                        "total_ms=%.1f"
                    ),
                    connection.connection_id,
                    request.response_id.value,
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


tts_service = PregeneratedTtsService()