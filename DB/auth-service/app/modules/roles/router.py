from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.modules.auth.model import User
from app.modules.roles.schema import PermissionGroup, RolePublic
from app.modules.roles.service import get_all_roles, get_role_domains

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RolePublic])
async def list_roles(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_roles(db)


@router.get("/permissions", response_model=list[PermissionGroup])
async def list_permissions(
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await get_role_domains(db)
