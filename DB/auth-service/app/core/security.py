from datetime import UTC, datetime, timedelta
from uuid import uuid4

import bcrypt
from jose import jwt

from app.core.config import settings

# bcrypt operates on a maximum of 72 bytes; truncate deterministically so
# hashing and verifying stay consistent (bcrypt 4.1+ raises on longer input).
_BCRYPT_MAX_BYTES = 72


def _encode(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_encode(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_encode(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> tuple[str, str]:
    """Return (token, jti). A unique jti is generated unless one is supplied."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    jti = to_encode.setdefault("jti", uuid4().hex)
    return (
        jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm),
        jti,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
