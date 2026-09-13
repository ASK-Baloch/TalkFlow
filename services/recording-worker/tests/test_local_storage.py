import asyncio
from pathlib import Path

from app.storage.local import (
    LocalRecordingStorage,
)


def test_local_storage(
    tmp_path: Path,
):
    async def run():
        source = tmp_path / "source.wav"

        source.write_bytes(b"test")

        storage = LocalRecordingStorage(root=str(tmp_path / "storage"))

        result = await storage.store(
            call_id=("96cfeefd-fc31-4ac7-b856-74f7ff717ab8"),
            source=source,
        )

        assert result.provider == "local"

        assert Path(result.storage_key).exists()

    asyncio.run(run())
