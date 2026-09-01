from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.realtime.asr.metrics import asr_metrics
from app.realtime.asr.service import asr_service
from app.realtime.audiosocket.manager import session_manager
from app.realtime.audiosocket.metrics import audiosocket_metrics
from app.realtime.audiosocket.server import audiosocket_server
from app.realtime.qualification.metrics import qualification_metrics
from app.realtime.qualification.service import qualification_service
from app.realtime.vad.metrics import vad_metrics
from app.realtime.vad.service import vad_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    await vad_service.start()

    await asr_service.start()

    await qualification_service.start()

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

        await qualification_service.stop()


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
    asr_ready = not asr_service.enabled or getattr(asr_service, "is_ready", False)
    qualification_ready = (
        not qualification_service.enabled or qualification_service.engine is not None
    )

    if not vad_ready or not asr_ready or not qualification_ready:
        return {
            "status": "not_ready",
            "vad": "ready" if vad_ready else "not_ready",
            "asr": "ready" if asr_ready else "not_ready",
            "qualification": "ready" if qualification_ready else "not_ready",
        }

    return {
        "status": "ready",
        "audiosocket": "ready",
        "vad": ("ready" if vad_service.enabled else "disabled"),
        "asr": ("ready" if asr_service.enabled else "disabled"),
        "qualification": ("ready" if qualification_service.enabled else "disabled"),
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
        "ready": asr_service.enabled and asr_service.scheduler is not None,
        "provider": "faster_whisper",
        "model": asr_service.settings.asr_model if asr_service.enabled else None,
        "device": asr_service.settings.asr_device if asr_service.enabled else None,
        "compute_type": asr_service.settings.asr_compute_type
        if asr_service.enabled
        else None,
        "queue_size": asr_service.scheduler.queue.qsize()
        if asr_service.enabled and asr_service.scheduler
        else 0,
        "workers": asr_service.settings.asr_workers if asr_service.enabled else 0,
        "active_sessions": asr_metrics.active_sessions,
        "partials_emitted": asr_metrics.partials_emitted,
        "finals_emitted": asr_metrics.finals_emitted,
        "stale_partials_dropped": asr_metrics.stale_partials_dropped,
        "decode_errors": asr_metrics.decode_errors,
        "partial_decode_average_ms": round(asr_metrics.partial_decode_average_ms(), 3),
        "partial_decode_p95_ms": round(asr_metrics.partial_decode_p95_ms(), 3),
        "final_decode_average_ms": round(asr_metrics.final_decode_average_ms(), 3),
        "final_decode_p95_ms": round(asr_metrics.final_decode_p95_ms(), 3),
    }


@app.get("/internal/qualification/status")
async def qualification_status():
    return {
        "enabled": qualification_service.enabled,
        "active_sessions": qualification_metrics.active_sessions,
        "sessions_total": qualification_metrics.sessions_total,
        "transcripts_processed": qualification_metrics.transcripts_processed,
        "consent_accepts": qualification_metrics.consent_accepts,
        "consent_declines": qualification_metrics.consent_declines,
        "fields_extracted": qualification_metrics.fields_extracted,
        "clarifications": qualification_metrics.clarifications,
        "qualified": qualification_metrics.qualified,
        "disqualified": qualification_metrics.disqualified,
        "processing_errors": qualification_metrics.processing_errors,
    }


@app.get("/internal/qualification/session/{connection_id}")
async def qualification_session(connection_id: str):
    if not get_settings().qualification_debug_endpoints:
        raise HTTPException(
            status_code=403,
            detail="Diagnostics endpoint disabled. Set QUALIFICATION_DEBUG_ENDPOINTS=true.",
        )

    session = qualification_service.get_session(connection_id)

    if session is None:
        return {"found": False}

    return {
        "found": True,
        "connection_id": session.connection_id,
        "session_uuid": session.session_uuid,
        "state": session.state.value,
        "status": session.status.value,
        "lead": {
            "consent": session.lead.consent,
            "full_name": session.lead.full_name,
            "age": session.lead.age,
            "medicare_part_a": session.lead.medicare_part_a,
            "medicare_part_b": session.lead.medicare_part_b,
            "zip_code": session.lead.zip_code,
        },
        "transcript_count": session.transcript_count,
        "clarification_counts": {
            key.value: value for key, value in session.clarification_counts.items()
        },
    }


class QualificationTestRequest(BaseModel):
    connection_id: str
    text: str


@app.post("/internal/qualification/test")
async def qualification_test(request: QualificationTestRequest):
    if not get_settings().qualification_debug_endpoints:
        raise HTTPException(
            status_code=403,
            detail="Diagnostics endpoint disabled. Set QUALIFICATION_DEBUG_ENDPOINTS=true.",
        )

    await qualification_service.attach_session(connection_id=request.connection_id)

    result = await qualification_service.process_final_transcript(
        connection_id=request.connection_id,
        session_uuid=None,
        text=request.text,
    )

    if result is None:
        return {"processed": False}

    return {
        "processed": True,
        "state": result.state.value,
        "status": result.status.value,
        "action": result.action.action_type.value,
        "expected_field": (
            result.action.expected_field.value if result.action.expected_field else None
        ),
        "reason": result.action.reason,
        "fields_updated": [field.value for field in result.fields_updated],
        "lead": {
            "consent": result.lead.consent,
            "full_name": result.lead.full_name,
            "age": result.lead.age,
            "medicare_part_a": result.lead.medicare_part_a,
            "medicare_part_b": result.lead.medicare_part_b,
            "zip_code": result.lead.zip_code,
        },
    }
