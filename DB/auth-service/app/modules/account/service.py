from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.account.model import UserSession


def generate_token_id() -> str:
    return uuid4().hex


async def create_user_session(
    db: AsyncSession,
    user_id: int,
    token_id: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> UserSession:
    session = UserSession(
        user_id=user_id,
        token_id=token_id,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def revoke_user_session(db: AsyncSession, token_id: str) -> bool:
    result = await db.execute(
        select(UserSession).where(UserSession.token_id == token_id)
    )
    session = result.scalar_one_or_none()
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        await db.commit()
        return True
    return False


async def list_active_sessions(db: AsyncSession, user_id: int) -> list[UserSession]:
    result = await db.execute(
        select(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
        .order_by(UserSession.last_seen_at.desc())
    )
    return list(result.scalars().all())


async def touch_session(db: AsyncSession, token_id: str) -> None:
    result = await db.execute(
        select(UserSession).where(UserSession.token_id == token_id)
    )
    session = result.scalar_one_or_none()
    if session:
        session.last_seen_at = func.now()
        await db.commit()