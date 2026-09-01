from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QualificationMetrics:
    sessions_total: int = 0
    active_sessions: int = 0

    transcripts_processed: int = 0

    consent_accepts: int = 0
    consent_declines: int = 0

    fields_extracted: int = 0

    clarifications: int = 0

    qualified: int = 0
    disqualified: int = 0

    processing_errors: int = 0


qualification_metrics = QualificationMetrics()
