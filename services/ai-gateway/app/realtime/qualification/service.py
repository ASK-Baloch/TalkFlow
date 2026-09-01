from __future__ import annotations

import logging

from app.core.config import (
    get_settings,
)

from .engine import (
    QualificationEngine,
)
from .metrics import (
    qualification_metrics,
)
from .session import (
    QualificationSession,
)
from .types import (
    FieldName,
    QualificationResult,
    QualificationStatus,
)

logger = logging.getLogger("talkflow.qualification")


class QualificationService:
    def __init__(self) -> None:
        settings = get_settings()

        self.enabled = settings.qualification_enabled

        self.log_state_transitions = settings.qualification_log_state_transitions

        self.log_field_values = settings.qualification_log_field_values

        self.engine = QualificationEngine(
            min_age=(settings.qualification_min_age),
            zip_length=(settings.qualification_zip_length),
            max_clarifications_per_field=(
                settings.qualification_max_clarifications_per_field
            ),
        )

        self._sessions: dict[
            str,
            QualificationSession,
        ] = {}

        self._recent_sessions: dict[
            str,
            QualificationSession,
        ] = {}

    async def start(self) -> None:
        if not self.enabled:
            logger.info("Qualification engine disabled")

            return

        logger.info("Qualification engine ready")

    async def stop(self) -> None:
        self._sessions.clear()

        qualification_metrics.active_sessions = 0

    async def attach_session(
        self,
        *,
        connection_id: str,
        session_uuid: str | None = None,
    ) -> QualificationSession | None:
        if not self.enabled:
            return None

        existing = self._sessions.get(connection_id)

        if existing is not None:
            if session_uuid:
                existing.session_uuid = session_uuid

            return existing

        session = QualificationSession(
            connection_id=(connection_id),
            session_uuid=(session_uuid),
        )

        session.latest_action = self.engine.initial_action(session)

        self._sessions[connection_id] = session

        qualification_metrics.sessions_total += 1
        qualification_metrics.active_sessions += 1

        logger.info(
            ("Qualification session attached connection_id=%s uuid=%s"),
            connection_id,
            session_uuid,
        )

        return session

    async def detach_session(
        self,
        connection_id: str,
    ) -> None:
        session = self._sessions.pop(
            connection_id,
            None,
        )

        if session is None:
            return

        qualification_metrics.active_sessions = max(
            0,
            qualification_metrics.active_sessions - 1,
        )

        # Keep the last 50 sessions for post-call debugging
        self._recent_sessions[connection_id] = session
        if len(self._recent_sessions) > 50:
            oldest_key = next(iter(self._recent_sessions))
            del self._recent_sessions[oldest_key]

        logger.info(
            (
                "Qualification session detached "
                "connection_id=%s "
                "status=%s "
                "transcripts=%s"
            ),
            connection_id,
            session.status.value,
            session.transcript_count,
        )

    async def process_final_transcript(
        self,
        *,
        connection_id: str,
        session_uuid: str | None,
        text: str,
    ) -> QualificationResult | None:
        if not self.enabled:
            return None

        session = self._sessions.get(connection_id)

        if session is None:
            session = await self.attach_session(
                connection_id=(connection_id),
                session_uuid=(session_uuid),
            )

        if session is None:
            return None

        if session_uuid:
            session.session_uuid = session_uuid

        old_state = session.state

        try:
            result = self.engine.process_transcript(
                session=session,
                text=text,
            )

        except Exception:
            qualification_metrics.processing_errors += 1

            logger.exception(
                ("Qualification processing failed connection_id=%s uuid=%s"),
                connection_id,
                session_uuid,
            )

            return None

        qualification_metrics.transcripts_processed += 1

        if FieldName.CONSENT in result.fields_updated:
            if result.lead.consent:
                qualification_metrics.consent_accepts += 1
            else:
                qualification_metrics.consent_declines += 1

        qualification_metrics.fields_extracted += len(
            [field for field in result.fields_updated if field != FieldName.CONSENT]
        )

        if result.action.action_type.value.startswith("clarify_"):
            qualification_metrics.clarifications += 1

        if result.status == QualificationStatus.QUALIFIED and old_state != result.state:
            qualification_metrics.qualified += 1

        if (
            result.status == QualificationStatus.DISQUALIFIED
            and old_state != result.state
        ):
            qualification_metrics.disqualified += 1

        if self.log_state_transitions and old_state != result.state:
            logger.info(
                (
                    "Qualification state transition "
                    "connection_id=%s "
                    "from=%s to=%s "
                    "action=%s"
                ),
                connection_id,
                old_state.value,
                result.state.value,
                result.action.action_type.value,
            )

        if self.log_field_values:
            logger.info(
                ("Qualification fields updated connection_id=%s fields=%s"),
                connection_id,
                [field.value for field in result.fields_updated],
            )

        session.latest_action = result.action

        return result

    def get_session(
        self,
        connection_id: str,
    ) -> QualificationSession | None:
        return self._sessions.get(connection_id) or self._recent_sessions.get(connection_id)

    @property
    def active_sessions(
        self,
    ) -> int:
        return len(self._sessions)


qualification_service = QualificationService()
