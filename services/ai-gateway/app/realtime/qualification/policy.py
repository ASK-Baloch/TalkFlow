from __future__ import annotations

from dataclasses import dataclass

from .types import LeadData


@dataclass(slots=True)
class QualificationPolicyResult:
    complete: bool

    qualified: bool | None

    reason: str | None


class MedicareQualificationPolicy:
    def __init__(
        self,
        *,
        min_age: int,
    ) -> None:
        self.min_age = min_age

    def evaluate(
        self,
        lead: LeadData,
    ) -> QualificationPolicyResult:
        if lead.consent is False:
            return QualificationPolicyResult(
                complete=True,
                qualified=False,
                reason="consent_declined",
            )

        if lead.consent is not True:
            return QualificationPolicyResult(
                complete=False,
                qualified=None,
                reason=None,
            )

        # Early deterministic disqualification.
        if lead.age is not None and lead.age < self.min_age:
            return QualificationPolicyResult(
                complete=True,
                qualified=False,
                reason="age_below_minimum",
            )

        if lead.medicare_part_a is False and lead.medicare_part_b is False:
            return QualificationPolicyResult(
                complete=True,
                qualified=False,
                reason="medicare_requirement_failed",
            )

        medicare_satisfied = (
            lead.medicare_part_a is True or lead.medicare_part_b is True
        )

        medicare_resolved = medicare_satisfied or (
            lead.medicare_part_a is False and lead.medicare_part_b is False
        )

        required_complete = all(
            (
                lead.full_name,
                lead.age is not None,
                medicare_resolved,
                lead.zip_code,
            )
        )

        if not required_complete:
            return QualificationPolicyResult(
                complete=False,
                qualified=None,
                reason=None,
            )

        qualified = lead.age >= self.min_age and medicare_satisfied

        return QualificationPolicyResult(
            complete=True,
            qualified=qualified,
            reason=("all_requirements_met" if qualified else "requirements_not_met"),
        )
