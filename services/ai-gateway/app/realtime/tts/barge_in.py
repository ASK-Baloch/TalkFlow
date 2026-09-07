from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("talkflow.barge_in")


@dataclass(slots=True)
class BargeInConfig:
    enabled: bool = True

    grace_ms: int = 0

    log_events: bool = True


class BargeInController:
    def __init__(
        self,
        *,
        tts_service,
        config: BargeInConfig,
    ) -> None:
        self.tts_service = tts_service

        self.config = config

    async def on_speech_start(
        self,
        *,
        connection_id: str,
    ) -> bool:
        if not self.config.enabled:
            return False

        if not await self.tts_service.is_playing(connection_id):
            return False

        if self.config.grace_ms > 0:
            elapsed_ms = await self.tts_service.playback_age_ms(connection_id)

            if elapsed_ms is not None and elapsed_ms < self.config.grace_ms:
                return False

        interrupted = await self.tts_service.interrupt(
            connection_id=(connection_id),
            reason=("caller_speech_start"),
        )

        if interrupted and self.config.log_events:
            logger.info(
                "Caller barge-in connection_id=%s",
                connection_id,
            )

        return interrupted
