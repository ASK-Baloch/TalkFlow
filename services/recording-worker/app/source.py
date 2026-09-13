from __future__ import annotations

import asyncio
from pathlib import Path

import asyncssh

from .call_id import (
    validate_call_id,
)
from .config import Settings


class AsteriskRecordingSource:
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self.settings = settings

    def remote_path(
        self,
        call_id: str,
    ) -> str:
        safe_call_id = validate_call_id(call_id)

        root = self.settings.recording_asterisk_dir.rstrip("/")

        return f"{root}/{safe_call_id}.{self.settings.recording_format}"

    async def _connect(
        self,
    ):
        return await asyncssh.connect(
            self.settings.asterisk_sftp_host,
            port=(self.settings.asterisk_sftp_port),
            username=(self.settings.asterisk_sftp_username),
            client_keys=[self.settings.asterisk_sftp_private_key],
            passphrase=(self.settings.asterisk_sftp_passphrase),
            known_hosts=(self.settings.asterisk_sftp_known_hosts),
        )

    async def wait_until_stable(
        self,
        *,
        call_id: str,
    ) -> str:
        remote_path = self.remote_path(call_id)

        loop = asyncio.get_running_loop()

        started = loop.time()

        previous_size: int | None = None

        stable_checks = 0

        while True:
            elapsed = loop.time() - started

            if elapsed > (self.settings.recording_max_wait_seconds):
                raise TimeoutError(f"Recording did not become stable: {remote_path}")

            try:
                async with (
                    await self._connect() as connection,
                    connection.start_sftp_client() as sftp,
                ):
                    stat = await sftp.stat(remote_path)

                    size = int(stat.size or 0)

            except (OSError, asyncssh.Error) as e:
                import logging

                logging.getLogger("talkflow.recording_worker").error(
                    f"SFTP error while polling Asterisk: {e}"
                )
                stable_checks = 0

                await asyncio.sleep(
                    self.settings.recording_stable_check_interval_seconds
                )

                continue

            if size <= 0:
                stable_checks = 0

            elif previous_size is not None and size == previous_size:
                stable_checks += 1

            else:
                stable_checks = 0

            previous_size = size

            if stable_checks >= (self.settings.recording_stable_checks_required):
                return remote_path

            await asyncio.sleep(self.settings.recording_stable_check_interval_seconds)

    async def fetch(
        self,
        *,
        remote_path: str,
        destination: Path,
    ) -> None:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        async with (
            await self._connect() as connection,
            connection.start_sftp_client() as sftp,
        ):
            await sftp.get(
                remote_path,
                str(destination),
            )
