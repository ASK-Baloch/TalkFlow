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

    DYNAMIC = "dynamic"


@dataclass(slots=True)
class PlannedResponse:
    route: TTSRoute

    response_id: str | None = None

    text: str | None = None


class ResponsePlanner:
    def plan_action(
        self,
        action: ConversationAction,
    ) -> PlannedResponse | None:
        response = response_for_action(action.action_type)

        if response is None:
            return None

        return PlannedResponse(
            route=(TTSRoute.PREGENERATED),
            response_id=(response.response_id.value),
        )

    def plan_dynamic(
        self,
        text: str,
    ) -> PlannedResponse:
        cleaned = text.strip()

        if not cleaned:
            raise ValueError("Dynamic TTS text cannot be empty")

        return PlannedResponse(
            route=TTSRoute.DYNAMIC,
            text=cleaned,
        )


response_planner = ResponsePlanner()
