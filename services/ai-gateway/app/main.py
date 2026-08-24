from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    yield


app = FastAPI(
    title="TalkFlow AI Gateway",
    version="0.1.0",
    lifespan=lifespan,
)


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
    }
