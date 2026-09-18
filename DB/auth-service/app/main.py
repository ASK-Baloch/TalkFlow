from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import async_session_factory
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.roles.router import router as roles_router
from app.modules.roles.service import seed_roles, seed_super_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_factory() as db:
        await seed_roles(db)
        await seed_super_admin(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(roles_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth-service"}
