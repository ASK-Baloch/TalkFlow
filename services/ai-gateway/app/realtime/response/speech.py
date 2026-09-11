from __future__ import annotations

from app.realtime.speech.types import (
    SpeechNormalizationContext,
)
from app.realtime.tts.planner import (
    PlannedResponse,
    TTSRoute,
)


class ResponseSpeechProcessor:
    def __init__(
        self,
        *,
        speech_service,
    ) -> None:
        self.speech_service = speech_service

    def process(
        self,
        planned: PlannedResponse,
        *,
        expected_field: str | None = None,
        provider_name: str | None = None,
    ) -> PlannedResponse:
        if planned.route == TTSRoute.PREGENERATED:
            return planned

        text = planned.tts_text or planned.display_text or ""

        if not text:
            return planned

        normalized = self.speech_service.normalize(
            text,
            context=(
                SpeechNormalizationContext(
                    expected_field=(expected_field),
                    provider_name=(provider_name),
                )
            ),
        )

        return PlannedResponse(
            route=planned.route,
            response_id=(planned.response_id),
            display_text=(planned.display_text or text),
            tts_text=(normalized.tts_text),
        )
