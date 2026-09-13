"""add call recordings

Revision ID: 41960d8b814f
Revises: f3365f07c9e2
Create Date: 2026-09-13 03:38:32.292298

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "41960d8b814f"
down_revision: str | Sequence[str] | None = "f3365f07c9e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS call_recordings (
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
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_call_recordings_status ON call_recordings(status);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_call_recordings_call_id ON call_recordings(call_id);"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX ix_call_recordings_call_id;")
    op.execute("DROP INDEX ix_call_recordings_status;")
    op.execute("DROP TABLE call_recordings;")
