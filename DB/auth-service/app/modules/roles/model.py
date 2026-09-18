import enum

from sqlalchemy import Boolean, Column, ForeignKey, Index, String, Table
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RoleDomain(str, enum.Enum):
    system = "system"
    operations = "operations"
    quality = "quality"
    verification = "verification"
    reporting = "reporting"


# Many-to-many association table — the only user/role link, no legacy FK column.
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_user_roles_user_id", "user_id"),
    Index("ix_user_roles_role_id", "role_id"),
    # `uq_single_master_admin` also lives on this table: a partial unique
    # index enforcing a single MASTER_ADMIN row, created via raw SQL in
    # migration b2f8c91d3e45 because its WHERE clause pins a specific role
    # UUID resolved at migration time — not expressible as static metadata.
)


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    domain: Mapped[RoleDomain] = mapped_column(
        SAEnum(
            RoleDomain,
            name="roledomain",
            native_enum=False,
            length=32,
            validate_strings=True,
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    assigned_users = relationship(
        "User", secondary="user_roles", back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r} domain={self.domain.value}>"
