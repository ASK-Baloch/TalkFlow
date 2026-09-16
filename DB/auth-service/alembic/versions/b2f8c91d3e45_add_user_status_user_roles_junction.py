"""add user_status user_roles junction

Revision ID: b2f8c91d3e45
Revises: 61a3de7a6070
Create Date: 2026-09-14 21:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2f8c91d3e45"
down_revision: Union[str, Sequence[str], None] = "61a3de7a6070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create userstatus enum type
    userstatus = sa.Enum("PENDING", "APPROVED", "REJECTED", name="userstatus")
    userstatus.create(op.get_bind(), checkfirst=True)

    # 2. Add status column to users (default PENDING)
    op.add_column(
        "users",
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="userstatus"),
            nullable=False,
            server_default="PENDING",
        ),
    )

    # 3. Backfill existing users to APPROVED
    op.execute("UPDATE users SET status = 'APPROVED'")

    # 4. Drop the server default after backfill so new rows use the ORM default
    op.alter_column("users", "status", server_default=None)

    # 5. Create user_roles junction table
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # 6. Create indexes on the junction table
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"], unique=False)
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"], unique=False)

    # 7. Backfill existing users.role_id into user_roles
    op.execute(
        """
        INSERT INTO user_roles (user_id, role_id)
        SELECT id, role_id
        FROM users
        WHERE role_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )

    # 8. Partial unique index: enforce single MASTER_ADMIN
    #    Resolve the MASTER_ADMIN role id at migration time.
    op.execute(
        """
        DO $$
        DECLARE
            master_id INTEGER;
        BEGIN
            SELECT id INTO master_id FROM roles WHERE name = 'MASTER_ADMIN' LIMIT 1;
            IF master_id IS NOT NULL THEN
                EXECUTE format(
                    'CREATE UNIQUE INDEX uq_single_master_admin ON user_roles (role_id) WHERE role_id = %s',
                    master_id
                );
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    # Drop partial unique index (can't drop by name easily in all PG versions, use raw)
    op.execute("DROP INDEX IF EXISTS uq_single_master_admin")

    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_column("users", "status")

    sa.Enum(name="userstatus").drop(op.get_bind(), checkfirst=True)
