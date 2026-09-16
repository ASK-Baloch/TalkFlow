import enum

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoleDomain(str, enum.Enum):
    system = "system"
    operations = "operations"
    quality = "quality"
    verification = "verification"
    reporting = "reporting"


# Many-to-many association table
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    domain: Mapped[RoleDomain] = mapped_column(
        SAEnum(RoleDomain, name="roledomain", validate_strings=True),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    # Legacy back-ref from single-role FK
    users = relationship("User", back_populates="role", foreign_keys="[User.role_id]")

    # M2M back-ref
    assigned_users = relationship("User", secondary="user_roles", back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r} domain={self.domain.value}>"
