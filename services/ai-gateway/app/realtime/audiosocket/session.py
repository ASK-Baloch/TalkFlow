from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class AudioSocketSession:
    connection_id: str

    session_uuid: str | None = None

    remote_address: str | None = None

    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    audio_packets_received: int = 0
    audio_bytes_received: int = 0

    audio_packets_sent: int = 0
    audio_bytes_sent: int = 0

    dtmf_packets_received: int = 0

    terminated: bool = False
