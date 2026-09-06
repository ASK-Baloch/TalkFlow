from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import redis.asyncio as redis


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


ROOT = repository_root()


async def load_cache(
    *,
    redis_url: str,
    asset_dir: Path,
    prefix: str,
) -> None:
    manifest_path = (
        asset_dir / "manifest.json"
    )

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    version = manifest[
        "asset_version"
    ]

    client = redis.from_url(
        redis_url,
        decode_responses=False,
    )

    try:
        await client.ping()

        pipeline = client.pipeline(
            transaction=False
        )

        for (
            response_id,
            metadata,
        ) in manifest[
            "responses"
        ].items():
            pcm = (
                asset_dir
                / metadata["file"]
            ).read_bytes()

            key = (
                f"{prefix}:"
                f"{version}:"
                f"{response_id}"
            )

            pipeline.set(
                key,
                pcm,
            )

        pipeline.set(
            (
                f"{prefix}:"
                f"{version}:manifest"
            ),
            json.dumps(
                manifest,
                ensure_ascii=False,
            ).encode("utf-8"),
        )

        await pipeline.execute()

        print(
            f"Loaded "
            f"{len(manifest['responses'])} "
            f"TTS assets into Redis"
        )

    finally:
        await client.aclose()


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--redis-url",
        default=(
            "redis://127.0.0.1:6379/0"
        ),
    )

    parser.add_argument(
        "--asset-dir",
        default=(
            "assets/tts/talkflow-v1"
        ),
    )

    parser.add_argument(
        "--prefix",
        default="talkflow:tts",
    )

    args = parser.parse_args()

    asyncio.run(
        load_cache(
            redis_url=(
                args.redis_url
            ),
            asset_dir=(
                ROOT
                / args.asset_dir
            ).resolve(),
            prefix=args.prefix,
        )
    )


if __name__ == "__main__":
    main()