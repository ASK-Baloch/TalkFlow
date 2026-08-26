import asyncio
import logging
import uuid
from contextlib import suppress

from app.core.config import get_settings

from .constants import AudioSocketMessageType
from .manager import session_manager
from .metrics import audiosocket_metrics
from .protocol import (
    AudioSocketProtocolError,
    read_packet,
    write_packet,
)
from .session import AudioSocketSession


logger = logging.getLogger("talkflow.audiosocket")


class AudioSocketServer:
    def __init__(self) -> None:
        settings = get_settings()

        self.host = settings.audiosocket_host
        self.port = settings.audiosocket_port
        self.echo_enabled = settings.audiosocket_echo_enabled

        self._server: asyncio.AbstractServer | None = None

    async def start(self) -> None:
        if self._server is not None:
            return

        self._server = await asyncio.start_server(
            self._handle_connection,
            host=self.host,
            port=self.port,
        )

        addresses = ", ".join(
            str(sock.getsockname())
            for sock in self._server.sockets or []
        )

        logger.info(
            "AudioSocket server started host=%s port=%s addresses=%s",
            self.host,
            self.port,
            addresses,
        )

    async def stop(self) -> None:
        if self._server is None:
            return

        self._server.close()
        await self._server.wait_closed()
        self._server = None

        logger.info("AudioSocket server stopped")

    async def _handle_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        connection_id = str(uuid.uuid4())

        peer = writer.get_extra_info("peername")
        remote_address = str(peer)

        session = AudioSocketSession(
            connection_id=connection_id,
            remote_address=remote_address,
        )

        await session_manager.add(session)

        audiosocket_metrics.connections_total += 1
        audiosocket_metrics.active_connections += 1

        logger.info(
            "AudioSocket connected connection_id=%s remote=%s",
            connection_id,
            remote_address,
        )

        try:
            await self._connection_loop(
                session=session,
                reader=reader,
                writer=writer,
            )

        except asyncio.IncompleteReadError:
            logger.info(
                "AudioSocket peer disconnected connection_id=%s uuid=%s",
                connection_id,
                session.session_uuid,
            )

        except ConnectionResetError:
            logger.info(
                "AudioSocket connection reset connection_id=%s uuid=%s",
                connection_id,
                session.session_uuid,
            )

        except AudioSocketProtocolError:
            audiosocket_metrics.protocol_errors += 1

            logger.exception(
                "AudioSocket protocol error connection_id=%s",
                connection_id,
            )

        except Exception:
            logger.exception(
                "Unexpected AudioSocket error connection_id=%s",
                connection_id,
            )

        finally:
            session.terminated = True

            await session_manager.remove(connection_id)

            audiosocket_metrics.active_connections = max(
                0,
                audiosocket_metrics.active_connections - 1,
            )

            writer.close()

            with suppress(Exception):
                await writer.wait_closed()

            logger.info(
                (
                    "AudioSocket session closed "
                    "connection_id=%s uuid=%s "
                    "received_packets=%s received_bytes=%s "
                    "sent_packets=%s sent_bytes=%s"
                ),
                connection_id,
                session.session_uuid,
                session.audio_packets_received,
                session.audio_bytes_received,
                session.audio_packets_sent,
                session.audio_bytes_sent,
            )

    async def _connection_loop(
        self,
        session: AudioSocketSession,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        while True:
            packet = await read_packet(reader)

            message_type = packet.message_type
            payload = packet.payload

            if message_type == AudioSocketMessageType.TERMINATE:
                logger.info(
                    "AudioSocket terminate received uuid=%s",
                    session.session_uuid,
                )

                return

            if message_type == AudioSocketMessageType.UUID:
                self._handle_uuid(
                    session=session,
                    payload=payload,
                )

                continue

            if message_type == AudioSocketMessageType.DTMF:
                self._handle_dtmf(
                    session=session,
                    payload=payload,
                )

                continue

            if (
                AudioSocketMessageType.PCM_8K
                <= message_type
                <= AudioSocketMessageType.PCM_192K
            ):
                await self._handle_audio(
                    session=session,
                    writer=writer,
                    message_type=message_type,
                    payload=payload,
                )

                continue

            if message_type == AudioSocketMessageType.ERROR:
                logger.error(
                    "Asterisk AudioSocket error uuid=%s payload=%s",
                    session.session_uuid,
                    payload.hex(),
                )

                return

            logger.warning(
                "Unknown AudioSocket packet uuid=%s type=0x%02x length=%s",
                session.session_uuid,
                message_type,
                len(payload),
            )

    def _handle_uuid(
        self,
        session: AudioSocketSession,
        payload: bytes,
    ) -> None:
        if len(payload) != 16:
            raise AudioSocketProtocolError(
                f"UUID payload must be 16 bytes, got {len(payload)}"
            )

        session.session_uuid = str(uuid.UUID(bytes=payload))

        logger.info(
            "AudioSocket UUID registered connection_id=%s uuid=%s",
            session.connection_id,
            session.session_uuid,
        )

    def _handle_dtmf(
        self,
        session: AudioSocketSession,
        payload: bytes,
    ) -> None:
        session.dtmf_packets_received += 1

        digit = payload.decode(
            "ascii",
            errors="replace",
        )

        logger.info(
            "DTMF received uuid=%s digit=%s",
            session.session_uuid,
            digit,
        )

    async def _handle_audio(
        self,
        session: AudioSocketSession,
        writer: asyncio.StreamWriter,
        message_type: int,
        payload: bytes,
    ) -> None:
        session.audio_packets_received += 1
        session.audio_bytes_received += len(payload)

        audiosocket_metrics.audio_packets_received += 1
        audiosocket_metrics.audio_bytes_received += len(payload)

        if not self.echo_enabled:
            return

        # Phase 1 loopback:
        # send the same PCM frame back to Asterisk.
        await write_packet(
            writer,
            message_type=message_type,
            payload=payload,
        )

        session.audio_packets_sent += 1
        session.audio_bytes_sent += len(payload)

        audiosocket_metrics.audio_packets_sent += 1
        audiosocket_metrics.audio_bytes_sent += len(payload)


audiosocket_server = AudioSocketServer()