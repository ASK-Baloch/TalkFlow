from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging
from app.realtime.audiosocket.manager import session_manager
from app.realtime.audiosocket.metrics import audiosocket_metrics
from app.realtime.audiosocket.server import audiosocket_server
from app.realtime.vad.metrics import vad_metrics
from app.realtime.vad.service import vad_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    await vad_service.start()

    await audiosocket_server.start()

    try:
        yield

    finally:
        await audiosocket_server.stop()

        await vad_service.stop()


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
    vad_ready = not vad_service.enabled or vad_service.pool.ready

    if not vad_ready:
        return {
            "status": "not_ready",
            "vad": "not_ready",
        }

    return {
        "status": "ready",
        "audiosocket": "ready",
        "vad": ("ready" if vad_service.enabled else "disabled"),
    }


@app.get("/internal/vad/status")
async def vad_status():
    return {
        "enabled": vad_service.enabled,
        "ready": (vad_service.pool.ready if vad_service.enabled else False),
        "pool_size": (vad_service.pool.size if vad_service.enabled else 0),
        "pool_available": (vad_service.pool.available if vad_service.enabled else 0),
        "active_sessions": (vad_metrics.active_sessions),
        "sessions_total": (vad_metrics.sessions_total),
        "chunks_processed": (vad_metrics.chunks_processed),
        "speech_starts": (vad_metrics.speech_starts),
        "speech_ends": (vad_metrics.speech_ends),
        "max_speech_events": (vad_metrics.max_speech_events),
        "processing_errors": (vad_metrics.processing_errors),
        "capacity_errors": (vad_metrics.capacity_errors),
        "inference_average_ms": (
            round(
                vad_metrics.inference_average_ms(),
                3,
            )
        ),
        "inference_p95_ms": (
            round(
                vad_metrics.inference_p95_ms(),
                3,
            )
        ),
    }
