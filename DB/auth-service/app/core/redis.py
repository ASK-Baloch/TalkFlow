import json
import logging
import uuid

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)


# ── Role cache (list of role names per user) ──────────────────────────────


async def get_cached_user_roles(user_id: uuid.UUID) -> list[str] | None:
    try:
        cached = await redis_client.get(f"user_roles:{user_id}")
        return json.loads(cached) if cached else None
    except Exception:
        logger.warning("Redis unavailable in get_cached_user_roles", exc_info=True)
        return None


async def set_cached_user_roles(
    user_id: uuid.UUID, role_names: list[str], ttl: int | None = None
) -> None:
    try:
        await redis_client.setex(
            f"user_roles:{user_id}",
            ttl or settings.role_cache_ttl,
            json.dumps(role_names),
        )
    except Exception:
        logger.warning("Redis unavailable in set_cached_user_roles", exc_info=True)


async def clear_cached_user_roles(user_id: uuid.UUID) -> None:
    try:
        await redis_client.delete(f"user_roles:{user_id}")
    except Exception:
        logger.warning("Redis unavailable in clear_cached_user_roles", exc_info=True)


# ── Token blacklist ───────────────────────────────────────────────────────


async def is_token_blacklisted(jti: str) -> bool:
    try:
        return await redis_client.exists(f"blacklist:{jti}") == 1
    except Exception:
        logger.warning("Redis unavailable in is_token_blacklisted", exc_info=True)
        return False


async def blacklist_token(jti: str, ttl: int | None = None) -> None:
    try:
        await redis_client.setex(
            f"blacklist:{jti}", ttl or settings.token_blacklist_ttl, "revoked"
        )
    except Exception:
        logger.warning("Redis unavailable in blacklist_token", exc_info=True)


async def redis_ping() -> bool:
    try:
        return bool(await redis_client.ping())
    except Exception:
        return False
