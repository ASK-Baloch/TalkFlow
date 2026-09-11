from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.realtime.qualification.types import (
    ConversationAction,
)

from .catalog import (
    response_for_action,
)


class TTSRoute(str, Enum):
    PREGENERATED = "pregenerated"
    TEMPLATE = "template"
    DYNAMIC = "dynamic"


@dataclass(slots=True)
class PlannedResponse:
    route: TTSRoute

    response_id: str | None = None

    display_text: str | None = None

    tts_text: str | None = None


class ResponsePlanner:
    def plan_pregenerated(
        self,
        response_id: str,
    ) -> PlannedResponse:
        return PlannedResponse(
            route=TTSRoute.PREGENERATED,
            response_id=response_id,
        )

    def plan_template(
        self,
        text: str,
        response_id: str | None = None,
    ) -> PlannedResponse:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Template TTS text cannot be empty")

        return PlannedResponse(
            route=TTSRoute.TEMPLATE,
            response_id=response_id,
            display_text=cleaned,
            tts_text=cleaned,
        )

    def plan_dynamic(
        self,
        text: str,
    ) -> PlannedResponse:
        cleaned = text.strip()

        if not cleaned:
            raise ValueError("Dynamic text cannot be empty")

        return PlannedResponse(
            route=TTSRoute.DYNAMIC,
            display_text=cleaned,
            tts_text=cleaned,
        )

    def plan_action(
        self,
        action: ConversationAction,
    ) -> PlannedResponse | None:
        response = response_for_action(action.action_type)

        if response is None:
            return None

        # Prioritize PREGENERATED. If the catalog provides text but no actual audio file exists,
        # the TTSService handles falling back to DYNAMIC if the provider is dynamic.
        # However, Phase 9 requested to formalize the routes.
        # We will assume that if we are using the catalog, we should try PREGENERATED first,
        # but if we needed variables (which this simplified system doesn't have yet), we'd use TEMPLATE.
        # For now, catalog responses are PREGENERATED.
        return self.plan_pregenerated(response.response_id.value)


response_planner = ResponsePlanner()
