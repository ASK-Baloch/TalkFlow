from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import require_admin, require_roles
from app.core.redis import clear_cached_user_roles
from app.db.session import get_db
from app.modules.account.model import UserSession
from app.modules.auth.model import User, UserStatus
from app.modules.auth.schema import MessageResponse, UserPublic
from app.modules.auth.service import serialize_user
from app.modules.roles.model import Role, user_roles

router = APIRouter(prefix="/admin", tags=["admin"])


class ApproveRequest(BaseModel):
    role_ids: list[int]


class RejectRequest(BaseModel):
    reason: str | None = None


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    role_names: list[str] | None = None


# Roles that can be assigned during user approval. MASTER_ADMIN is intentionally
# excluded — it is reserved for the seed super-admin provisioned via .env.
APPROVABLE_ROLE_NAMES = {"DEVOPS_IT", "CAMPAIGN_MANAGER", "QA", "VIEWER"}


@router.get("/users", response_model=list[UserPublic])
async def list_users(
    user_status: UserStatus | None = Query(None, alias="status"),
    _admin: User = Depends(require_roles(["MASTER_ADMIN", "DEVOPS_IT"])),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(User).options(selectinload(User.roles), selectinload(User.role))
    if user_status:
        stmt = stmt.where(User.status == user_status)
    stmt = stmt.order_by(User.created_at.desc()) if hasattr(User, "created_at") else stmt.order_by(User.id.desc())
    result = await db.execute(stmt)
    users = list(result.scalars().all())
    return [serialize_user(u) for u in users]


@router.patch("/users/{user_id}/approve", response_model=UserPublic)
async def approve_user(
    user_id: int,
    payload: ApproveRequest,
    _admin: User = Depends(require_roles(["MASTER_ADMIN", "DEVOPS_IT"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.status == UserStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already approved")

    # Reject MASTER_ADMIN role assignment via this endpoint
    master_role_result = await db.execute(
        select(Role).where(Role.name == "MASTER_ADMIN")
    )
    master_role = master_role_result.scalar_one_or_none()
    if master_role and master_role.id in payload.role_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign MASTER_ADMIN role through approval",
        )

    # Validate all role ids exist
    if payload.role_ids:
        roles_result = await db.execute(
            select(Role).where(Role.id.in_(payload.role_ids))
        )
        valid_roles = list(roles_result.scalars().all())
        if len(valid_roles) != len(payload.role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more role IDs are invalid",
            )
        disallowed = [
            r.name for r in valid_roles if r.name not in APPROVABLE_ROLE_NAMES
        ]
        if disallowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role(s) cannot be assigned during approval: {', '.join(sorted(disallowed))}",
            )

    # Update user status
    user.status = UserStatus.APPROVED

    # Clear existing M2M roles
    await db.execute(
        user_roles.delete().where(user_roles.c.user_id == user.id)
    )

    # Insert new roles
    for role_id in payload.role_ids:
        await db.execute(
            user_roles.insert().values(user_id=user.id, role_id=role_id)
        )

    # Also set legacy role_id to the first assigned role (if any)
    if payload.role_ids:
        user.role_id = payload.role_ids[0]

    await db.commit()

    user_id = user.id

    # Expire the identity-mapped instance so selectinload actually refetches
    # the (now populated) M2M roles instead of reusing the stale empty collection.
    db.expire_all()

    # Reload with relationships
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles), selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.scalar_one()

    # Clear Redis cache
    await clear_cached_user_roles(user.id)

    return serialize_user(user)


@router.patch("/users/{user_id}/reject", response_model=MessageResponse)
async def reject_user(
    user_id: int,
    _admin: User = Depends(require_roles(["MASTER_ADMIN", "DEVOPS_IT"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.status == UserStatus.REJECTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already rejected")

    user.status = UserStatus.REJECTED
    await db.commit()
    await clear_cached_user_roles(user.id)

    return MessageResponse(message="User has been rejected")


@router.patch("/users/{user_id}/update", response_model=UserPublic)
async def update_user_record(
    user_id: int,
    payload: UpdateUserRequest,
    admin: User = Depends(require_roles(["MASTER_ADMIN", "DEVOPS_IT"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles), selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    admin_role_names = [r.name for r in admin.roles] if admin.roles else []
    caller_is_master = "MASTER_ADMIN" in admin_role_names

    # Uniqueness checks (only when the value actually changes)
    if payload.username is not None and payload.username != user.username:
        dup = await db.execute(select(User).where(User.username == payload.username))
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists",
            )
        user.username = payload.username

    if payload.email is not None and payload.email.lower() != (user.email or "").lower():
        dup = await db.execute(select(User).where(User.email == payload.email))
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        user.email = payload.email

    if payload.first_name is not None or payload.last_name is not None:
        current = (user.full_name or "").split(maxsplit=1)
        first = payload.first_name if payload.first_name is not None else (current[0] if current else "")
        last = payload.last_name if payload.last_name is not None else (current[1] if len(current) > 1 else "")
        user.full_name = (" ".join(p for p in (first, last) if p)) or None

    if payload.is_active is not None:
        user.is_active = payload.is_active

    # Role replacement — validated, never silently dropped
    if payload.role_names is not None:
        new_names = list(dict.fromkeys(payload.role_names))
        roles_result = await db.execute(select(Role).where(Role.name.in_(new_names)))
        valid_roles = list(roles_result.scalars().all())
        valid_names = {r.name for r in valid_roles}
        missing = [n for n in new_names if n not in valid_names]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown role(s): {', '.join(sorted(missing))}",
            )

        user_has_master = "MASTER_ADMIN" in {r.name for r in user.roles}
        if "MASTER_ADMIN" in new_names and not caller_is_master:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a MASTER_ADMIN can grant the MASTER_ADMIN role",
            )
        if user_has_master and "MASTER_ADMIN" not in new_names:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the MASTER_ADMIN role from an administrator account",
            )
        if "MASTER_ADMIN" in new_names and not user_has_master:
            other_master = await db.execute(
                select(User.id)
                .join(user_roles)
                .join(Role)
                .where(Role.name == "MASTER_ADMIN", User.id != user.id)
                .limit(1)
            )
            if other_master.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Another account already holds the MASTER_ADMIN role",
                )

        # Preserve the caller-provided role order for the legacy role_id
        provided_order = {name: idx for idx, name in enumerate(new_names)}
        ordered_roles = sorted(valid_roles, key=lambda r: provided_order.get(r.name, 0))

        await db.execute(user_roles.delete().where(user_roles.c.user_id == user.id))
        for role in ordered_roles:
            await db.execute(
                user_roles.insert().values(user_id=user.id, role_id=role.id)
            )
        user.role_id = ordered_roles[0].id if ordered_roles else None
        user.is_admin = "MASTER_ADMIN" in valid_names

    await db.commit()

    user_id_capture = user.id
    db.expire_all()

    refreshed = await db.execute(
        select(User)
        .options(selectinload(User.roles), selectinload(User.role))
        .where(User.id == user_id_capture)
    )
    user = refreshed.scalar_one()

    await clear_cached_user_roles(user.id)
    return serialize_user(user)


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user_record(
    user_id: int,
    admin: User = Depends(require_roles(["MASTER_ADMIN", "DEVOPS_IT"])),
    db: AsyncSession = Depends(get_db),
):
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Remove dependent rows before deleting the user
    await db.execute(UserSession.__table__.delete().where(UserSession.user_id == user_id))
    await db.execute(user_roles.delete().where(user_roles.c.user_id == user_id))
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    await clear_cached_user_roles(user_id)

    return MessageResponse(message="User has been deleted")
