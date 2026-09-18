"""placeholder for untracked schema revision

The connected database's `alembic_version` table was already stamped at
this revision id when this repo caught up to it — its actual DDL was applied
directly against the database by a process outside this codebase, and the
migration that made those changes was never committed here, so it can't be
reproduced.

Comparing this repo's current models against the live database (via
`alembic.autogenerate.compare_metadata`) shows the net effect of that
untracked change was:

- `users`, `roles`, `user_sessions`, `user_roles`: primary keys converted
  from auto-increment integers to server-generated UUIDs
  (`gen_random_uuid()`).
- `users`, `roles`, `user_sessions`: gained `created_at`/`updated_at`
  audit columns (`clock_timestamp()` default).
- `users`: the legacy single-role `role_id` foreign key and the `is_admin`
  boolean were dropped — role assignment is now exclusively through the
  `user_roles` many-to-many table (see `app/modules/roles/model.py`).

This revision performs no schema changes of its own; it exists only so
Alembic has a local file for the id the database is already stamped at,
letting `alembic upgrade`/`alembic current` resolve cleanly again. The
current models (`app/modules/auth/model.py`, `app/modules/roles/model.py`,
`app/modules/account/model.py`) were written to describe the live schema
exactly and verified against the connected database before this file was
added.

Revision ID: d6e7f8a9b0c1
Revises: b2f8c91d3e45
Create Date: 2026-09-19 00:00:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "d6e7f8a9b0c1"
down_revision: Union[str, Sequence[str], None] = "b2f8c91d3e45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op placeholder — see module docstring."""
    pass


def downgrade() -> None:
    """No-op: this revision made no changes of its own to reverse."""
    pass
