from __future__ import annotations

from .extractors import (
    extract_fields,
)
from .policy import (
    MedicareQualificationPolicy,
)
from .session import (
    QualificationSession,
)
from .types import (
    ActionType,
    ConversationAction,
    ConversationState,
    FieldName,
    QualificationResult,
    QualificationStatus,
)
from .validators import (
    validate_age,
    validate_boolean,
    validate_name,
    validate_zip_code,
)


class QualificationEngine:
    def __init__(
        self,
        *,
        min_age: int,
        zip_length: int,
        max_clarifications_per_field: int,
    ) -> None:
        self.zip_length = zip_length

        self.max_clarifications_per_field = max_clarifications_per_field

        self.policy = MedicareQualificationPolicy(min_age=min_age)

    def initial_action(
        self,
        session: QualificationSession,
    ) -> ConversationAction:
        return ConversationAction(
            action_type=ActionType.ASK_CONSENT,
            state=session.state,
            qualification_status=session.status,
            expected_field=FieldName.CONSENT,
        )

    def process_transcript(
        self,
        *,
        session: QualificationSession,
        text: str,
    ) -> QualificationResult:
        session.transcript_count += 1
        session.touch()

        if session.status != (QualificationStatus.IN_PROGRESS):
            return self._terminal_result(session)

        extracted = extract_fields(
            text,
            state=session.state,
        )

        updated_fields: list[FieldName] = []

        # ====================================================
        # Consent is a hard gate.
        # ====================================================

        if session.state == ConversationState.WAITING_FOR_CONSENT:
            if extracted.consent is None:
                return self._clarification(
                    session,
                    field_name=FieldName.CONSENT,
                    action_type=(ActionType.CLARIFY_CONSENT),
                )

            session.lead.consent = extracted.consent

            updated_fields.append(FieldName.CONSENT)

            session.reset_clarification(FieldName.CONSENT)

            if extracted.consent is False:
                session.state = ConversationState.CONSENT_DECLINED

                session.status = QualificationStatus.CONSENT_DECLINED

                return QualificationResult(
                    state=session.state,
                    status=session.status,
                    lead=session.lead,
                    fields_updated=(updated_fields),
                    action=ConversationAction(
                        action_type=(ActionType.CONSENT_DECLINED),
                        state=session.state,
                        qualification_status=(session.status),
                        reason="consent_declined",
                    ),
                )

        # At this point consent must be true.
        if session.lead.consent is not True:
            return self._clarification(
                session,
                field_name=FieldName.CONSENT,
                action_type=(ActionType.CLARIFY_CONSENT),
            )

        # Determine if this utterance contains explicit correction intent
        import re

        from .normalization import normalize_text

        normalized_text = normalize_text(text)
        is_correction = bool(
            re.search(r"\b(?:actually|sorry|correction|no)\b", normalized_text)
        )

        # ====================================================
        # Apply valid fields from same/current utterance.
        # ====================================================

        if extracted.full_name is not None and validate_name(extracted.full_name):
            if session.lead.full_name is None or is_correction:
                if session.lead.full_name != extracted.full_name:
                    session.lead.full_name = extracted.full_name
                    updated_fields.append(FieldName.FULL_NAME)
            session.reset_clarification(FieldName.FULL_NAME)

        if extracted.age is not None and validate_age(extracted.age):
            if session.lead.age is None or is_correction:
                if session.lead.age != extracted.age:
                    session.lead.age = extracted.age
                    updated_fields.append(FieldName.AGE)
            session.reset_clarification(FieldName.AGE)

        if validate_boolean(extracted.medicare_part_a):
            if session.lead.medicare_part_a is None or is_correction:
                if session.lead.medicare_part_a != extracted.medicare_part_a:
                    session.lead.medicare_part_a = extracted.medicare_part_a
                    updated_fields.append(FieldName.MEDICARE_PART_A)
            session.reset_clarification(FieldName.MEDICARE_PART_A)

        if validate_boolean(extracted.medicare_part_b):
            if session.lead.medicare_part_b is None or is_correction:
                if session.lead.medicare_part_b != extracted.medicare_part_b:
                    session.lead.medicare_part_b = extracted.medicare_part_b
                    updated_fields.append(FieldName.MEDICARE_PART_B)
            session.reset_clarification(FieldName.MEDICARE_PART_B)

        if extracted.zip_code is not None and validate_zip_code(
            extracted.zip_code,
            expected_length=(self.zip_length),
        ):
            if session.lead.zip_code is None or is_correction:
                if session.lead.zip_code != extracted.zip_code:
                    session.lead.zip_code = extracted.zip_code
                    updated_fields.append(FieldName.ZIP_CODE)
            session.reset_clarification(FieldName.ZIP_CODE)

        # ====================================================
        # Qualification/disqualification evaluation.
        # ====================================================

        policy_result = self.policy.evaluate(session.lead)

        if policy_result.complete:
            if policy_result.qualified:
                session.state = ConversationState.QUALIFIED

                session.status = QualificationStatus.QUALIFIED

                return QualificationResult(
                    state=session.state,
                    status=session.status,
                    lead=session.lead,
                    fields_updated=(updated_fields),
                    action=ConversationAction(
                        action_type=(ActionType.QUALIFIED),
                        state=session.state,
                        qualification_status=(session.status),
                        reason=(policy_result.reason),
                    ),
                )

            session.state = ConversationState.DISQUALIFIED

            session.status = QualificationStatus.DISQUALIFIED

            return QualificationResult(
                state=session.state,
                status=session.status,
                lead=session.lead,
                fields_updated=(updated_fields),
                action=ConversationAction(
                    action_type=(ActionType.DISQUALIFIED),
                    state=session.state,
                    qualification_status=(session.status),
                    reason=(policy_result.reason),
                ),
            )

        # ====================================================
        # Select next missing field.
        # ====================================================

        action = self._next_action(
            session,
            text=text,
            updated_fields=(updated_fields),
        )

        return QualificationResult(
            state=session.state,
            status=session.status,
            lead=session.lead,
            fields_updated=updated_fields,
            action=action,
        )

    def _next_action(
        self,
        session: QualificationSession,
        *,
        text: str,
        updated_fields: list[FieldName],
    ) -> ConversationAction:
        if session.lead.full_name is None:
            return self._ask_or_clarify(
                session,
                field_name=(FieldName.FULL_NAME),
                state=(ConversationState.COLLECTING_NAME),
                ask_type=(ActionType.ASK_NAME),
                clarify_type=(ActionType.CLARIFY_NAME),
                updated_fields=(updated_fields),
            )

        if session.lead.age is None:
            return self._ask_or_clarify(
                session,
                field_name=FieldName.AGE,
                state=(ConversationState.COLLECTING_AGE),
                ask_type=(ActionType.ASK_AGE),
                clarify_type=(ActionType.CLARIFY_AGE),
                updated_fields=(updated_fields),
            )

        medicare_satisfied = (
            session.lead.medicare_part_a is True or session.lead.medicare_part_b is True
        )

        if not medicare_satisfied:
            if (
                session.lead.medicare_part_a is None
                and session.lead.medicare_part_b is None
            ):
                return self._ask_or_clarify(
                    session,
                    field_name=(FieldName.MEDICARE_PART_A),
                    state=(ConversationState.COLLECTING_PART_A),
                    ask_type=(ActionType.ASK_PART_A),
                    clarify_type=(ActionType.CLARIFY_PART_A),
                    updated_fields=(updated_fields),
                )

            if (
                session.lead.medicare_part_a is False
                and session.lead.medicare_part_b is None
            ):
                return self._ask_or_clarify(
                    session,
                    field_name=(FieldName.MEDICARE_PART_B),
                    state=(ConversationState.COLLECTING_PART_B),
                    ask_type=(ActionType.ASK_PART_B),
                    clarify_type=(ActionType.CLARIFY_PART_B),
                    updated_fields=(updated_fields),
                )

        if session.lead.zip_code is None:
            return self._ask_or_clarify(
                session,
                field_name=(FieldName.ZIP_CODE),
                state=(ConversationState.COLLECTING_ZIP),
                ask_type=(ActionType.ASK_ZIP),
                clarify_type=(ActionType.CLARIFY_ZIP),
                updated_fields=(updated_fields),
            )

        # Normally the policy should have completed
        # before reaching this point.
        return ConversationAction(
            action_type=(ActionType.NO_ACTION),
            state=session.state,
            qualification_status=(session.status),
        )

    def _ask_or_clarify(
        self,
        session: QualificationSession,
        *,
        field_name: FieldName,
        state: ConversationState,
        ask_type: ActionType,
        clarify_type: ActionType,
        updated_fields: list[FieldName],
    ) -> ConversationAction:
        was_already_asking = session.state == state

        session.state = state
        session.touch()

        if was_already_asking and field_name not in updated_fields:
            return self._clarification(
                session,
                field_name=field_name,
                action_type=clarify_type,
            ).action

        return ConversationAction(
            action_type=ask_type,
            state=session.state,
            qualification_status=(session.status),
            expected_field=field_name,
        )

    def _clarification(
        self,
        session: QualificationSession,
        *,
        field_name: FieldName,
        action_type: ActionType,
    ) -> QualificationResult:
        count = session.increment_clarification(field_name)

        action = ConversationAction(
            action_type=action_type,
            state=session.state,
            qualification_status=(session.status),
            expected_field=field_name,
            metadata={
                "clarification_count": count,
                "max_clarifications": (self.max_clarifications_per_field),
            },
        )

        return QualificationResult(
            state=session.state,
            status=session.status,
            lead=session.lead,
            action=action,
        )

    def _terminal_result(
        self,
        session: QualificationSession,
    ) -> QualificationResult:
        if session.status == QualificationStatus.QUALIFIED:
            action_type = ActionType.QUALIFIED

        elif session.status == QualificationStatus.CONSENT_DECLINED:
            action_type = ActionType.CONSENT_DECLINED

        else:
            action_type = ActionType.DISQUALIFIED

        return QualificationResult(
            state=session.state,
            status=session.status,
            lead=session.lead,
            action=ConversationAction(
                action_type=action_type,
                state=session.state,
                qualification_status=(session.status),
            ),
        )
