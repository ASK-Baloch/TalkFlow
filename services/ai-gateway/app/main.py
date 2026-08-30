from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging
from app.realtime.asr.metrics import asr_metrics
from app.realtime.asr.service import asr_service
from app.realtime.audiosocket.manager import session_manager
from app.realtime.audiosocket.metrics import audiosocket_metrics
from app.realtime.audiosocket.server import audiosocket_server
from app.realtime.vad.metrics import vad_metrics
from app.realtime.vad.service import vad_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    await vad_service.start()

    await asr_service.start()

    await audiosocket_server.start()

    try:
        yield

    finally:
        await audiosocket_server.stop()

        # Stop ASR after audiosocket stops accepting calls, so ongoing processing can wind down or cancel
        # Currently we don't have an explicit asr_service.stop() method implemented but we will call it if it exists
        if hasattr(asr_service, "stop"):
            await asr_service.stop()

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


@app.get("/internal/asr/status")
async def asr_status():
    return {
        "enabled": asr_service.enabled,
        "provider": "faster_whisper",
        "model": asr_service.settings.asr_model if asr_service.enabled else None,
        "device": asr_service.settings.asr_device if asr_service.enabled else None,
        "active_sessions": asr_metrics.active_sessions,
        "queue_size": asr_service.scheduler.queue.qsize()
        if asr_service.enabled and asr_service.scheduler
        else 0,
        "partials_emitted": asr_metrics.partials_emitted,
        "finals_emitted": asr_metrics.finals_emitted,
        "stale_partials_dropped": asr_metrics.stale_partials_dropped,
        "decode_errors": asr_metrics.decode_errors,
        "partial_decode_average_ms": round(asr_metrics.partial_decode_average_ms(), 3),
        "partial_decode_p95_ms": round(asr_metrics.partial_decode_p95_ms(), 3),
        "final_decode_average_ms": round(asr_metrics.final_decode_average_ms(), 3),
        "final_decode_p95_ms": round(asr_metrics.final_decode_p95_ms(), 3),
    }
