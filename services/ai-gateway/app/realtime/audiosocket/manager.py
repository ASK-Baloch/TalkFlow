import asyncio

from .session import AudioSocketSession


class AudioSocketSessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, AudioSocketSession] = {}
        self._lock = asyncio.Lock()

    async def add(
        self,
        session: AudioSocketSession,
    ) -> None:
        async with self._lock:
            self._sessions[session.connection_id] = session

    async def remove(
        self,
        connection_id: str,
    ) -> AudioSocketSession | None:
        async with self._lock:
            return self._sessions.pop(connection_id, None)

    async def get(
        self,
        connection_id: str,
    ) -> AudioSocketSession | None:
        async with self._lock:
            return self._sessions.get(connection_id)

    async def count(self) -> int:
        async with self._lock:
            return len(self._sessions)


session_manager = AudioSocketSessionManager()
