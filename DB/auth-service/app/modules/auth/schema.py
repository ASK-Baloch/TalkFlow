from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.auth.model import UserStatus


class LoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class PinLoginRequest(BaseModel):
    email: str = Field(min_length=1)
    collaborator_pin: str = Field(min_length=4, max_length=4)


class RegisterRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=6)
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    type: str = Field(default="Reporting User", min_length=1)
    extension: str | None = None


class SignupRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=6)
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    extension: str | None = None


class UserPublic(BaseModel):
    id: UUID
    username: str | None = None
    email: str
    firstName: str | None = None
    lastName: str | None = None
    full_name: str | None = None
    type: str | None = None
    role: str | None = None
    role_domain: str | None = None
    roles: list[str] = []
    extension: str | None = None
    status: str = "active"
    account_status: UserStatus = UserStatus.PENDING
    is_admin: bool = False
    is_active: bool = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class MessageResponse(BaseModel):
    message: str


class UpdateProfileRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    username: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    extension: str | None = Field(default=None, max_length=40)


class ProfileUpdateResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    user: UserPublic
