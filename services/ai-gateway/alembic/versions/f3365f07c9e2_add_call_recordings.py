"""add call recordings

Revision ID: f3365f07c9e2
Revises:
Create Date: 2026-09-12 13:35:59.735436

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3365f07c9e2"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE call_recordings (
            id UUID PRIMARY KEY,
            call_id UUID NOT NULL UNIQUE,
            status VARCHAR(32) NOT NULL,
            source VARCHAR(32) NOT NULL,
            source_path TEXT,
            storage_provider VARCHAR(32),
            storage_key TEXT,
            format VARCHAR(16) NOT NULL,
            size_bytes BIGINT,
            duration_ms BIGINT,
            sample_rate INTEGER,
            channels INTEGER,
            sha256 CHAR(64),
            ended_at TIMESTAMPTZ,
            available_at TIMESTAMPTZ,
            retention_until TIMESTAMPTZ,
            error_code VARCHAR(64),
            error_message TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)

    op.execute("""
        CREATE INDEX ix_call_recordings_status
        ON call_recordings(status);
    """)

    op.execute("""
        CREATE INDEX ix_call_recordings_available_at
        ON call_recordings(available_at);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX ix_call_recordings_available_at;")
    op.execute("DROP INDEX ix_call_recordings_status;")
    op.execute("DROP TABLE call_recordings;")
