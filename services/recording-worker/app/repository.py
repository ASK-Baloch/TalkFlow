from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import uuid4

import asyncpg


class RecordingRepository:
    def __init__(
        self,
        *,
        database_url: str,
        retention_days: int,
    ) -> None:
        self.database_url = database_url

        self.retention_days = retention_days

        self.pool: asyncpg.Pool | None = None

    async def start(self) -> None:
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,
            max_size=5,
        )

    async def stop(self) -> None:
        if self.pool is None:
            return

        await self.pool.close()

        self.pool = None

    def _require_pool(
        self,
    ) -> asyncpg.Pool:
        if self.pool is None:
            raise RuntimeError("RecordingRepository not started")

        return self.pool

    async def ensure_pending(
        self,
        *,
        call_id: str,
        source_path: str,
        ended_at: datetime,
    ) -> None:
        pool = self._require_pool()

        retention_until = datetime.now(timezone.utc) + timedelta(
            days=(self.retention_days)
        )

        async with pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO call_recordings (
                    id,
                    call_id,
                    status,
                    source,
                    source_path,
                    format,
                    ended_at,
                    retention_until
                )
                VALUES (
                    $1,
                    $2,
                    'PENDING',
                    'asterisk',
                    $3,
                    'wav',
                    $4,
                    $5
                )
                ON CONFLICT (call_id)
                DO NOTHING
                """,
                uuid4(),
                call_id,
                source_path,
                ended_at,
                retention_until,
            )

    async def set_status(
        self,
        *,
        call_id: str,
        status: str,
    ) -> None:
        pool = self._require_pool()

        async with pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE call_recordings

                SET
                    status = $2,
                    updated_at = NOW()

                WHERE
                    call_id = $1
                """,
                call_id,
                status,
            )

    async def mark_ready(
        self,
        *,
        call_id: str,
        storage_provider: str,
        storage_key: str,
        size_bytes: int,
        duration_ms: int,
        sample_rate: int,
        channels: int,
        sha256: str,
    ) -> None:
        pool = self._require_pool()

        async with pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE call_recordings

                SET
                    status = 'READY',
                    storage_provider = $2,
                    storage_key = $3,
                    size_bytes = $4,
                    duration_ms = $5,
                    sample_rate = $6,
                    channels = $7,
                    sha256 = $8,
                    available_at = NOW(),
                    error_code = NULL,
                    error_message = NULL,
                    updated_at = NOW()

                WHERE
                    call_id = $1
                """,
                call_id,
                storage_provider,
                storage_key,
                size_bytes,
                duration_ms,
                sample_rate,
                channels,
                sha256,
            )

    async def mark_failed(
        self,
        *,
        call_id: str,
        error_code: str,
        error_message: str,
    ) -> None:
        pool = self._require_pool()

        async with pool.acquire() as connection:
            await connection.execute(
                """
                UPDATE call_recordings

                SET
                    status = 'FAILED',
                    error_code = $2,
                    error_message = $3,
                    updated_at = NOW()

                WHERE
                    call_id = $1
                """,
                call_id,
                error_code,
                error_message[:2000],
            )
