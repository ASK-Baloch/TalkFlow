import enum

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    extension: Mapped[str | None] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    collaborator_pin: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, name="userstatus", validate_strings=True),
        default=UserStatus.PENDING,
        nullable=False,
    )

    # Legacy single-role FK — kept for backward-compat; prefer `roles` M2M.
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users", foreign_keys=[role_id])

    # M2M roles through junction table
    roles = relationship("Role", secondary="user_roles", back_populates="assigned_users")

    sessions = relationship("UserSession", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
