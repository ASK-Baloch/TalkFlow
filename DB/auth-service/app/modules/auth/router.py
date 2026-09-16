from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_jti, get_current_user
from app.core.redis import blacklist_token
from app.core.security import create_access_token
from app.db.session import get_db
from app.modules.account.service import (
    create_user_session,
    generate_token_id,
    revoke_user_session,
    touch_session,
)
from app.modules.auth.model import User, UserStatus
from app.modules.auth.schema import (
    LoginRequest,
    MessageResponse,
    PinLoginRequest,
    ProfileUpdateResponse,
    RegisterRequest,
    SignupRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserPublic,
)
from app.modules.auth.service import (
    authenticate_pin,
    authenticate_user,
    get_user_by_email,
    refresh_user_role_cache,
    register_user,
    serialize_user,
    signup_user,
    update_user_profile,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_context(request: Request) -> tuple[str | None, str | None]:
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    return user_agent, ip_address


def _ensure_login_allowed(user: User) -> None:
    """Only fully approved accounts may authenticate and receive a token."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Please contact an administrator.",
        )
    if user.status == UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is awaiting administrator approval. Please try again later.",
        )
    if user.status == UserStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account request was rejected. Please contact an administrator.",
        )


async def _issue_token(
    db: AsyncSession, user: User, request: Request, token_id: str
) -> TokenResponse:
    access_token, _jti = create_access_token({"sub": user.email, "jti": token_id})
    user_agent, ip_address = _client_context(request)
    await create_user_session(db, user.id, token_id, user_agent, ip_address)
    fresh = await get_user_by_email(db, user.email)
    await refresh_user_role_cache(db, fresh)
    return TokenResponse(access_token=access_token, user=serialize_user(fresh))


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    _ensure_login_allowed(user)
    return await _issue_token(db, user, request, generate_token_id())


@router.post("/pin-login", response_model=TokenResponse)
async def pin_login(
    payload: PinLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_pin(db, payload.email, payload.collaborator_pin)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or PIN",
        )
    _ensure_login_allowed(user)
    return await _issue_token(db, user, request, generate_token_id())


@router.post("/register", response_model=TokenResponse)
async def register(
    payload: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await register_user(db, payload)
    return await _issue_token(db, user, request, generate_token_id())


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    await signup_user(db, payload)
    return MessageResponse(
        message="Account created successfully! Your request has been sent to the administrators for approval."
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    jti: str = Depends(get_current_jti),
    db: AsyncSession = Depends(get_db),
):
    await blacklist_token(jti)
    await revoke_user_session(db, jti)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserPublic)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await refresh_user_role_cache(db, current_user)
    return serialize_user(current_user)


@router.patch("/me", response_model=ProfileUpdateResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    old_email = current_user.email
    await update_user_profile(db, current_user, payload)

    fresh = await get_user_by_email(db, current_user.email)
    if fresh is None:
        fresh = current_user

    if fresh.email != old_email:
        # Re-issue a token so the JWT (which embeds the old email) stays valid.
        access_token, _jti = create_access_token(
            {"sub": fresh.email, "jti": generate_token_id()}
        )
        await refresh_user_role_cache(db, fresh)
        return ProfileUpdateResponse(
            access_token=access_token, user=serialize_user(fresh)
        )

    await refresh_user_role_cache(db, fresh)
    return ProfileUpdateResponse(user=serialize_user(fresh))
