import enum

from sqlalchemy import Boolean, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    extension: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    collaborator_pin: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[UserStatus] = mapped_column(
        SAEnum(
            UserStatus,
            name="userstatus",
            native_enum=False,
            length=16,
            validate_strings=True,
        ),
        default=UserStatus.PENDING,
        nullable=False,
    )

    # Roles are assigned exclusively through the `roles` M2M relationship —
    # there is no single-role column on this table.
    roles = relationship(
        "Role", secondary="user_roles", back_populates="assigned_users"
    )

    sessions = relationship("UserSession", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
