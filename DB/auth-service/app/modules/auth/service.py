from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis import clear_cached_user_roles, set_cached_user_roles
from app.core.security import hash_password, verify_password
from app.modules.auth.model import User, UserStatus
from app.modules.auth.schema import (
    RegisterRequest,
    SignupRequest,
    UpdateProfileRequest,
    UserPublic,
)
from app.modules.roles.model import Role, user_roles


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.roles))
        .where(User.email == email.lower().strip())
    )
    return result.scalar_one_or_none()


async def find_role_by_name(db: AsyncSession, name: str) -> Role | None:
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def authenticate_pin(db: AsyncSession, email: str, pin: str) -> User | None:
    user = await get_user_by_email(db, email)
    if not user or not user.collaborator_pin or not verify_password(
        pin, user.collaborator_pin
    ):
        return None
    return user


# Normalize dashboard "Account TYPE" options to seeded system role names.
ROLE_NAME_ALIASES = {
    "Admin": "DEVOPS_IT",
    "Campaign Manager": "CAMPAIGN_MANAGER",
    "Licensed Agent": "VIEWER",
    "QA": "QA",
    "Verifier": "VIEWER",
    "Reporting User": "REPORTING_USER",
    "Master Admin": "MASTER_ADMIN",
}


async def register_user(db: AsyncSession, payload: RegisterRequest) -> User:
    """Legacy register — assigns a role via the type field, status=APPROVED."""
    email = payload.email.lower().strip()
    existing = await get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    role = await find_role_by_name(db, ROLE_NAME_ALIASES.get(payload.type, payload.type))
    parts = [p for p in (payload.first_name, payload.last_name) if p]
    full_name = " ".join(parts) or payload.username or email.split("@")[0]

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=full_name,
        username=payload.username or email.split("@")[0],
        extension=payload.extension,
        is_admin=False,
        is_active=True,
        status=UserStatus.APPROVED,
        role=role,
    )
    db.add(user)
    await db.flush()

    # Also insert into the M2M junction for backward compat
    if role:
        await db.execute(
            user_roles.insert().values(user_id=user.id, role_id=role.id)
        )

    await db.commit()
    await db.refresh(user)
    return user


async def signup_user(db: AsyncSession, payload: SignupRequest) -> User:
    """New signup — no role assigned, status=PENDING."""
    email = payload.email.lower().strip()
    existing = await get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    parts = [p for p in (payload.first_name, payload.last_name) if p]
    full_name = " ".join(parts) or payload.username or email.split("@")[0]

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=full_name,
        username=payload.username or email.split("@")[0],
        extension=payload.extension,
        is_admin=False,
        is_active=True,
        status=UserStatus.PENDING,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_profile(
    db: AsyncSession, user: User, payload: UpdateProfileRequest
) -> User:
    """Apply editable profile fields. Returns True if email changed (token re-issue needed)."""
    if payload.first_name is not None or payload.last_name is not None:
        existing_parts = (user.full_name or "").split(maxsplit=1)
        first = (
            payload.first_name
            if payload.first_name is not None
            else (existing_parts[0] if existing_parts else "")
        )
        last = (
            payload.last_name
            if payload.last_name is not None
            else (existing_parts[1] if len(existing_parts) > 1 else "")
        )
        user.full_name = " ".join(p for p in (first, last) if p) or None

    if payload.username is not None:
        user.username = payload.username

    if payload.extension is not None:
        user.extension = payload.extension or None

    if payload.email is not None and payload.email.lower().strip() != user.email.lower():
        new_email = payload.email.lower().strip()
        existing = await get_user_by_email(db, new_email)
        if existing is not None and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        user.email = new_email

    await db.commit()
    return user


async def refresh_user_role_cache(db: AsyncSession, user: User) -> None:
    """Cache the list of role names for this user."""
    # Ensure roles are loaded
    if not user.roles:
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user.id)
        )
        fresh = result.scalar_one_or_none()
        if fresh:
            user = fresh

    role_names = [r.name for r in user.roles] if user.roles else []
    if role_names:
        await set_cached_user_roles(user.id, role_names)
    else:
        await clear_cached_user_roles(user.id)


def serialize_user(user: User) -> UserPublic:
    email = user.email
    full_name = user.full_name or ""
    parts = full_name.split(maxsplit=1)
    first = parts[0] if parts else (user.username or email.split("@")[0])
    last = parts[1] if len(parts) > 1 else ""

    # M2M roles
    role_names = [r.name for r in user.roles] if user.roles else []

    # Legacy single-role fallback
    legacy_role = user.role.name if user.role else (role_names[0] if role_names else None)
    domain = user.role.domain.value if user.role else None

    return UserPublic(
        id=user.id,
        username=user.username or email.split("@")[0],
        email=email,
        firstName=first,
        lastName=last or "",
        full_name=full_name or None,
        type=legacy_role or "REPORTING_USER",
        role=legacy_role,
        role_domain=domain,
        roles=role_names,
        extension=user.extension,
        status="active" if user.is_active else "inactive",
        account_status=user.status,
        is_admin="MASTER_ADMIN" in role_names,
        is_active=user.is_active,
    )
