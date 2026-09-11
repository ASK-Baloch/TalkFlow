from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.registry import registry
from app.realtime.asr.metrics import asr_metrics
from app.realtime.asr.service import AsrService
from app.realtime.audiosocket.manager import session_manager
from app.realtime.audiosocket.metrics import audiosocket_metrics
from app.realtime.audiosocket.server import audiosocket_server
from app.realtime.llm.service import LLMService
from app.realtime.qualification.metrics import qualification_metrics
from app.realtime.qualification.service import qualification_service
from app.realtime.tts.metrics import tts_metrics
from app.realtime.tts.service import TTSService
from app.realtime.vad.metrics import vad_metrics
from app.realtime.vad.service import vad_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    from app.realtime.providers.loader import create_provider

    settings = get_settings()

    stt_provider = create_provider(
        settings.stt_provider_class,
        settings=settings,
    )

    pregenerated_provider = create_provider(
        settings.tts_pregenerated_provider_class,
        settings=settings,
    )

    dynamic_provider = create_provider(
        settings.tts_dynamic_provider_class,
        settings=settings,
    )

    llm_provider = create_provider(
        settings.llm_provider_class,
        settings=settings,
    )

    if hasattr(stt_provider, "start"):
        await stt_provider.start()

    if hasattr(pregenerated_provider, "start"):
        await pregenerated_provider.start()

    if hasattr(dynamic_provider, "start"):
        await dynamic_provider.start()

    registry.asr_service = AsrService(provider=stt_provider)
    registry.tts_service = TTSService(
        enabled=settings.tts_enabled,
        pregenerated_provider=pregenerated_provider,
        dynamic_provider=dynamic_provider,
        sample_rate=settings.tts_sample_rate,
        sample_width_bytes=2,
        frame_ms=20,
        queue_size=10,
        interrupt_enabled=True,
        flush_queue_on_interrupt=True,
        drop_stale_audio=True,
        barge_in_log_events=True,
    )
    registry.llm_service = LLMService(
        provider=llm_provider,
        enabled=settings.llm_enabled,
        max_tokens=(settings.llm_max_tokens),
        temperature=(settings.llm_temperature),
        top_p=settings.llm_top_p,
        top_k=settings.llm_top_k,
        presence_penalty=(settings.llm_presence_penalty),
        enable_thinking=(settings.llm_enable_thinking),
        max_history_turns=(settings.llm_max_history_turns),
        max_input_chars=(settings.llm_max_input_chars),
    )

    from app.realtime.tts.barge_in import BargeInConfig, BargeInController

    registry.barge_in_controller = BargeInController(
        tts_service=registry.tts_service,
        config=BargeInConfig(
            enabled=getattr(settings, "barge_in_enabled", True),
            grace_ms=getattr(settings, "barge_in_grace_ms", 0),
            log_events=getattr(settings, "barge_in_log_events", True),
        ),
    )

    from app.realtime.speech.lexicon import PronunciationLexicon
    from app.realtime.speech.normalizer import SpeechNormalizer
    from app.realtime.speech.service import SpeechNormalizationService

    speech_lexicon = PronunciationLexicon.from_file(
        settings.speech_pronunciation_lexicon
    )

    speech_normalizer = SpeechNormalizer(
        lexicon=speech_lexicon,
        normalize_zip_codes=settings.speech_normalize_zip_codes,
        normalize_phone_numbers=settings.speech_normalize_phone_numbers,
        normalize_currency=settings.speech_normalize_currency,
        normalize_percentages=settings.speech_normalize_percentages,
        normalize_numbers=settings.speech_normalize_numbers,
        strip_markdown=settings.speech_strip_markdown,
        collapse_whitespace=settings.speech_collapse_whitespace,
        provider_adapter_enabled=settings.speech_provider_adapter_enabled,
        max_text_chars=settings.speech_max_text_chars,
    )

    registry.speech_service = SpeechNormalizationService(
        normalizer=speech_normalizer,
        enabled=settings.speech_normalization_enabled,
        log_normalization=settings.speech_log_normalization,
    )

    from app.realtime.response.speech import ResponseSpeechProcessor
    from app.realtime.response.stream_assembler import (
        SentenceStreamAssembler,
        StreamAssemblerConfig,
    )
    from app.realtime.response.streaming import StreamingResponseOrchestrator
    from app.realtime.tts.planner import response_planner

    speech_processor = ResponseSpeechProcessor(speech_service=registry.speech_service)

    registry.streaming_response_orchestrator = StreamingResponseOrchestrator(
        llm_service=registry.llm_service,
        response_planner=response_planner,
        tts_service=registry.tts_service,
        speech_processor=speech_processor,
        assembler_factory=lambda: SentenceStreamAssembler(
            config=StreamAssemblerConfig()
        ),
    )

    from app.realtime.conversation.turn_controller import ConversationTurnController

    registry.turn_controller = ConversationTurnController(
        llm_service=registry.llm_service,
        tts_service=registry.tts_service,
        response_orchestrator=registry.streaming_response_orchestrator,
    )

    await vad_service.start()
    await registry.asr_service.start()
    await qualification_service.start()
    await registry.tts_service.start()
    await registry.llm_service.start()
    await audiosocket_server.start()

    try:
        yield

    finally:
        await audiosocket_server.stop()

        await registry.llm_service.stop()

        await registry.tts_service.stop()

        if hasattr(registry.asr_service, "stop"):
            await registry.asr_service.stop()

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
    asr_ready = not registry.asr_service.enabled or getattr(
        registry.asr_service, "is_ready", False
    )
    qualification_ready = (
        not qualification_service.enabled or qualification_service.engine is not None
    )
    tts_ready = not registry.tts_service.enabled or getattr(
        registry.tts_service, "enabled", False
    )

    if not vad_ready or not asr_ready or not qualification_ready or not tts_ready:
        return {
            "status": "not_ready",
            "vad": "ready" if vad_ready else "not_ready",
            "asr": "ready" if asr_ready else "not_ready",
            "qualification": "ready" if qualification_ready else "not_ready",
            "tts": "ready" if tts_ready else "not_ready",
        }

    return {
        "status": "ready",
        "audiosocket": "ready",
        "vad": ("ready" if vad_service.enabled else "disabled"),
        "asr": ("ready" if registry.asr_service.enabled else "disabled"),
        "qualification": ("ready" if qualification_service.enabled else "disabled"),
        "tts": ("ready" if registry.tts_service.enabled else "disabled"),
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
        "enabled": registry.asr_service.enabled,
        "ready": registry.asr_service.enabled
        and registry.asr_service.scheduler is not None,
        "provider": "faster_whisper",
        "model": registry.asr_service.settings.asr_model
        if registry.asr_service.enabled
        else None,
        "device": registry.asr_service.settings.asr_device
        if registry.asr_service.enabled
        else None,
        "compute_type": registry.asr_service.settings.asr_compute_type
        if registry.asr_service.enabled
        else None,
        "queue_size": registry.asr_service.scheduler.queue.qsize()
        if registry.asr_service.enabled and registry.asr_service.scheduler
        else 0,
        "workers": registry.asr_service.settings.asr_workers
        if registry.asr_service.enabled
        else 0,
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


@app.get("/internal/tts/status")
async def tts_status():
    return {
        "enabled": (registry.tts_service.enabled),
        "mode": "pregenerated",
        "asset_version": (get_settings().tts_asset_version),
        "sample_rate": (get_settings().tts_sample_rate),
        "connected_calls": (registry.tts_service.connected_calls),
        "active_playbacks": (tts_metrics.active_playbacks),
        "requests_total": (tts_metrics.requests_total),
        "completed_total": (tts_metrics.completed_total),
        "playback_errors": (tts_metrics.playback_errors),
        "queue_overflows": (tts_metrics.queue_overflows),
        "assets_missing": (tts_metrics.assets_missing),
        "barge_in_enabled": (get_settings().barge_in_enabled),
        "interruptions_total": (tts_metrics.interruptions_total),
        "interrupted_playbacks_total": (tts_metrics.interrupted_playbacks_total),
        "flushed_requests_total": (tts_metrics.flushed_requests_total),
        "stale_requests_dropped_total": (tts_metrics.stale_requests_dropped_total),
        "stale_chunks_dropped_total": (tts_metrics.stale_chunks_dropped_total),
        "barge_in_cancel_average_ms": (
            round(
                tts_metrics.average_barge_in_cancel_ms(),
                3,
            )
        ),
        "barge_in_cancel_p95_ms": (
            round(
                tts_metrics.p95_barge_in_cancel_ms(),
                3,
            )
        ),
        "first_audio_average_ms": (
            round(
                tts_metrics.average_first_audio_ms(),
                3,
            )
        ),
        "first_audio_p95_ms": (
            round(
                tts_metrics.p95_first_audio_ms(),
                3,
            )
        ),
    }


class TTSDynamicRequest(BaseModel):
    connection_id: str
    text: str


@app.post("/internal/tts/dynamic")
async def tts_dynamic_test(request: TTSDynamicRequest):
    from app.realtime.tts.planner import response_planner

    planned = response_planner.plan_dynamic(request.text)
    success = await registry.tts_service.enqueue(
        connection_id=request.connection_id,
        planned=planned,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to play text")
    return {"success": True}


class TTSTestRequest(BaseModel):
    connection_id: str
    response_id: str


@app.post("/internal/tts/test-playback")
async def tts_test_playback(request: TTSTestRequest):
    settings = get_settings()
    if not getattr(settings, "qualification_debug_endpoints", False):
        raise HTTPException(status_code=403, detail="Diagnostics endpoint disabled.")

    from app.realtime.tts.planner import PlannedResponse, TTSRoute

    planned = PlannedResponse(
        route=TTSRoute.PREGENERATED,
        response_id=request.response_id,
    )

    success = await registry.tts_service.enqueue(
        connection_id=request.connection_id,
        planned=planned,
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to enqueue test playback")

    return {"success": True}


@app.get("/internal/llm/status")
async def llm_status():
    settings = get_settings()
    from app.realtime.llm.metrics import llm_metrics

    return {
        "enabled": settings.llm_enabled,
        "model": settings.llm_model,
        "thinking": settings.llm_enable_thinking,
        "provider": await registry.llm_service.health(),
        "metrics": {
            "requests_total": llm_metrics.requests_total,
            "completed_total": llm_metrics.completed_total,
            "failures_total": llm_metrics.failures_total,
            "timeouts_total": llm_metrics.timeouts_total,
            "average_latency_ms": round(llm_metrics.average_latency_ms(), 2),
            "p95_latency_ms": round(llm_metrics.p95_latency_ms(), 2),
        },
    }


class LLMTestRequest(BaseModel):
    text: str


@app.post("/internal/llm/test")
async def llm_test(request: LLMTestRequest):
    settings = get_settings()
    if not getattr(settings, "llm_debug_endpoints", False):
        raise HTTPException(
            status_code=403,
            detail="Diagnostics endpoint disabled. Set LLM_DEBUG_ENDPOINTS=true.",
        )

    from app.realtime.llm.types import LLMFallbackContext

    context = LLMFallbackContext(
        connection_id="test",
        caller_text=request.text,
        current_state="qualification",
        expected_field="zip_code",
    )

    result = await registry.llm_service.generate_fallback(context)

    if not result:
        raise HTTPException(status_code=500, detail="LLM generation failed")

    return {
        "text": result.text,
        "model": result.model,
        "latency_ms": result.latency_ms,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
    }


class SpeechNormalizationRequest(BaseModel):
    text: str
    expected_field: str | None = None
    provider: str | None = None


@app.post("/internal/speech/normalize")
async def speech_normalize_test(request: SpeechNormalizationRequest):
    from app.realtime.speech.types import SpeechNormalizationContext

    context = SpeechNormalizationContext(
        expected_field=request.expected_field,
        provider_name=request.provider,
    )

    result = registry.speech_service.normalize(request.text, context=context)

    return {
        "display_text": result.display_text,
        "tts_text": result.tts_text,
        "changed": result.changed,
        "rules_applied": result.rules_applied,
    }
