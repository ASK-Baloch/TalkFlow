from dataclasses import dataclass


@dataclass
class AudioSocketMetrics:
    connections_total: int = 0
    active_connections: int = 0

    audio_packets_received: int = 0
    audio_bytes_received: int = 0

    audio_packets_sent: int = 0
    audio_bytes_sent: int = 0

    protocol_errors: int = 0


audiosocket_metrics = AudioSocketMetrics()
