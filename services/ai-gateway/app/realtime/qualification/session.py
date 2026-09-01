from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter_ns

from .types import (
    ConversationAction,
    ConversationState,
    FieldName,
    LeadData,
    QualificationStatus,
)


@dataclass(slots=True)
class QualificationSession:
    connection_id: str

    session_uuid: str | None = None

    state: ConversationState = ConversationState.WAITING_FOR_CONSENT

    status: QualificationStatus = QualificationStatus.IN_PROGRESS

    lead: LeadData = field(default_factory=LeadData)

    latest_action: ConversationAction | None = None

    clarification_counts: dict[
        FieldName,
        int,
    ] = field(default_factory=dict)

    transcript_count: int = 0

    created_ns: int = field(default_factory=perf_counter_ns)

    updated_ns: int = field(default_factory=perf_counter_ns)

    def increment_clarification(
        self,
        field_name: FieldName,
    ) -> int:
        count = (
            self.clarification_counts.get(
                field_name,
                0,
            )
            + 1
        )

        self.clarification_counts[field_name] = count

        self.touch()

        return count

    def reset_clarification(
        self,
        field_name: FieldName,
    ) -> None:
        self.clarification_counts.pop(
            field_name,
            None,
        )

        self.touch()

    def touch(self) -> None:
        self.updated_ns = perf_counter_ns()
