from uuid import UUID

from pydantic import BaseModel


class RolePublic(BaseModel):
    id: UUID
    name: str
    domain: str
    description: str | None = None
    is_system: bool = False

    model_config = {"from_attributes": True}


class PermissionGroup(BaseModel):
    domain: str
    roles: list[str]
