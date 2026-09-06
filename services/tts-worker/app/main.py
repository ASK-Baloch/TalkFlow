from __future__ import annotations

from contextlib import (
    asynccontextmanager,
)

from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.responses import (
    StreamingResponse,
)

from .chatterbox_provider import (
    ChatterboxRuntime,
)
from .config import settings
from .schemas import (
    SynthesisRequest,
)

runtime = ChatterboxRuntime(
    settings
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    del app

    await runtime.start()

    try:
        yield

    finally:
        await runtime.stop()


app = FastAPI(
    title="TalkFlow TTS Worker",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {
        "ready": (
            runtime.model is not None
        ),
        "provider": (
            "chatterbox_turbo"
        ),
        "device": (
            settings.device
        ),
        "voice_id": (
            settings.voice_id
        ),
        "target_sample_rate": (
            settings
            .target_sample_rate
        ),
        "native_model_streaming": False,
    }


@app.post(
    "/v1/synthesize"
)
async def synthesize(
    request: SynthesisRequest,
):
    try:
        pcm = await runtime.synthesize(
            text=request.text,
            voice_id=(
                request.voice_id
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="TTS synthesis failed",
        ) from exc

    frame_bytes = 320

    async def iterator():
        offset = 0

        while offset < len(pcm):
            yield pcm[
                offset:
                offset
                + frame_bytes
            ]

            offset += (
                frame_bytes
            )

    return StreamingResponse(
        iterator(),
        media_type=(
            "application/octet-stream"
        ),
        headers={
            "X-Audio-Sample-Rate":
                "8000",
            "X-Audio-Channels":
                "1",
            "X-Audio-Format":
                "pcm_s16le",
        },
    )