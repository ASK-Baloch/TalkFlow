from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

import redis.asyncio as redis

from .types import (
    AudioAsset,
    ResponseId,
)

logger = logging.getLogger(
    "talkflow.tts.cache"
)

from app.core.config import get_settings


class TtsAssetCache:
    def __init__(
        self,
        *,
        prefix: str,
        version: str,
        asset_dir: str,
        cache_enabled: bool,
        local_fallback: bool,
    ) -> None:
        self.redis_url = get_settings().redis_url
        self.prefix = prefix
        self.version = version

        self.asset_dir = Path(
            asset_dir
        )

        self.cache_enabled = (
            cache_enabled
        )

        self.local_fallback = (
            local_fallback
        )

        self._redis = None

        self._manifest: dict | None = (
            None
        )

    async def start(
        self,
    ) -> None:
        self._load_manifest()

        if not self.cache_enabled:
            return

        self._redis = redis.from_url(
            self.redis_url,
            decode_responses=False,
        )

        try:
            await self._redis.ping()

        except Exception:
            logger.exception(
                "TTS Redis unavailable"
            )

            if not self.local_fallback:
                raise

            await self._redis.aclose()

            self._redis = None

    async def stop(
        self,
    ) -> None:
        if self._redis is not None:
            await self._redis.aclose()

            self._redis = None

    def _load_manifest(
        self,
    ) -> None:
        path = (
            self.asset_dir
            / "manifest.json"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"TTS manifest not found: {path}"
            )

        self._manifest = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if (
            self._manifest.get(
                "asset_version"
            )
            != self.version
        ):
            raise ValueError(
                "Configured TTS version "
                "does not match manifest"
            )

        if (
            self._manifest.get(
                "sample_rate"
            )
            != 8000
        ):
            raise ValueError(
                "Phase 5 assets must be 8kHz"
            )

        for metadata in self._manifest.get("responses", {}).values():
            pcm_path = self.asset_dir / metadata["file"]
            if not pcm_path.exists():
                raise FileNotFoundError(f"TTS asset missing: {pcm_path}")
            
            pcm = pcm_path.read_bytes()
            digest = hashlib.sha256(pcm).hexdigest()
            if digest != metadata["sha256"]:
                raise ValueError(f"TTS asset corrupted (checksum mismatch): {pcm_path}")

    def _key(
        self,
        response_id: ResponseId,
    ) -> str:
        return (
            f"{self.prefix}:"
            f"{self.version}:"
            f"{response_id.value}"
        )

    async def get(
        self,
        response_id: ResponseId,
    ) -> AudioAsset:
        if self._manifest is None:
            raise RuntimeError(
                "TTS cache not started"
            )

        metadata = self._manifest[
            "responses"
        ].get(
            response_id.value
        )

        if metadata is None:
            raise KeyError(
                f"Unknown TTS response: "
                f"{response_id.value}"
            )

        pcm: bytes | None = None

        if self._redis is not None:
            try:
                pcm = await self._redis.get(
                    self._key(
                        response_id
                    )
                )

            except Exception:
                logger.exception(
                    "TTS Redis read failed"
                )

        if (
            pcm is None
            and self.local_fallback
        ):
            pcm = (
                self.asset_dir
                / metadata["file"]
            ).read_bytes()

        if pcm is None:
            raise RuntimeError(
                f"TTS asset unavailable: "
                f"{response_id.value}"
            )

        digest = hashlib.sha256(
            pcm
        ).hexdigest()

        if digest != metadata[
            "sha256"
        ]:
            raise ValueError(
                f"TTS checksum mismatch: "
                f"{response_id.value}"
            )

        return AudioAsset(
            response_id=response_id,
            pcm=pcm,
            sample_rate=(
                self._manifest[
                    "sample_rate"
                ]
            ),
            channels=(
                self._manifest[
                    "channels"
                ]
            ),
            sample_width_bytes=(
                self._manifest[
                    "sample_width_bytes"
                ]
            ),
            sample_count=(
                metadata[
                    "sample_count"
                ]
            ),
            duration_ms=(
                metadata[
                    "duration_ms"
                ]
            ),
            sha256=digest,
        )