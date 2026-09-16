from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis import is_token_blacklisted
from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.auth.model import User, UserStatus
from app.modules.roles.model import user_roles, Role

security_scheme = HTTPBearer(auto_error=True)


async def _fetch_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.roles))
        .where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the JWT, check Redis revocation blacklist, load the active user."""
    try:
        payload = decode_access_token(credentials.credentials)
        email: str | None = payload.get("sub")
        jti: str | None = payload.get("jti")
        if not email or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired or is invalid",
        )

    if await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
        )

    user = await _fetch_user_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or not found",
        )

    if user.status != UserStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not approved",
        )

    return user


async def get_current_jti(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """Extract only the jti claim for revocation operations (logout, admin kill)."""
    try:
        payload = decode_access_token(credentials.credentials)
        jti: str | None = payload.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return jti
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired or is invalid",
        )


def _user_role_names(user: User) -> list[str]:
    """Return the list of role names for a user (M2M first, fallback to legacy FK)."""
    if user.roles:
        return [r.name for r in user.roles]
    if user.role:
        return [user.role.name]
    return []


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require MASTER_ADMIN via the M2M junction table."""
    role_names = _user_role_names(current_user)
    if "MASTER_ADMIN" not in role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def require_roles(allowed_names: list[str]):
    """Verify the user holds at least one of the allowed role names (via M2M)."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_names = _user_role_names(current_user)
        if not set(allowed_names).intersection(role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )
        return current_user

    return role_checker


def require_role(allowed_domains: list[str]):
    """Verify the user's role domain is in the allowed list (admins bypass)."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        role_names = _user_role_names(current_user)
        if "MASTER_ADMIN" in role_names:
            return current_user
        if not current_user.role or current_user.role.domain.value not in allowed_domains:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )
        return current_user

    return role_checker
