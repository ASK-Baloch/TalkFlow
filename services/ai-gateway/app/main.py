from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging
from app.realtime.audiosocket.manager import session_manager
from app.realtime.audiosocket.metrics import audiosocket_metrics
from app.realtime.audiosocket.server import audiosocket_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    await audiosocket_server.start()

    try:
        yield

    finally:
        await audiosocket_server.stop()


app = FastAPI(
    title="TalkFlow AI Gateway",
    version="0.2.0",
    lifespan=lifespan,
)
@app.get("/internal/audiosocket/status")
async def audiosocket_status():
    return {
        "active_connections": await session_manager.count(),
        "connections_total": audiosocket_metrics.connections_total,
        "audio_packets_received": audiosocket_metrics.audio_packets_received,
        "audio_bytes_received": audiosocket_metrics.audio_bytes_received,
        "audio_packets_sent": audiosocket_metrics.audio_packets_sent,
        "audio_bytes_sent": audiosocket_metrics.audio_bytes_sent,
        "protocol_errors": audiosocket_metrics.protocol_errors,
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ai-gateway",
    }


@app.get("/ready")
async def ready():
    return {
        "status": "ready",
        "audiosocket": "ready",
    }