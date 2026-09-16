from sqlalchemy import delete, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.modules.auth.model import User, UserStatus
from app.modules.roles.model import Role, RoleDomain, user_roles

LEGACY_ROLE_NAMES: dict[str, str] = {
    "Master Admin": "MASTER_ADMIN",
    "IT / DevOps": "DEVOPS_IT",
    "Campaign Manager": "CAMPAIGN_MANAGER",
    "QA Manager": "QA",
    "Verifier / Licensed Agent": "VIEWER",
    "Reporting User": "REPORTING_USER",
    "masterAdmin": "MASTER_ADMIN",
    "itDevOps": "DEVOPS_IT",
    "campaignManager": "CAMPAIGN_MANAGER",
    "qaManager": "QA",
    "verifierAgent": "VIEWER",
    "reportingUser": "REPORTING_USER",
}

ROLE_SEED: list[dict] = [
    {
        "name": "MASTER_ADMIN",
        "domain": RoleDomain.system,
        "description": "System administration, global settings, & full administrative privileges.",
        "is_system": True,
    },
    {
        "name": "DEVOPS_IT",
        "domain": RoleDomain.system,
        "description": "Technical infrastructure, telephony integrations & developer operations.",
        "is_system": True,
    },
    {
        "name": "CAMPAIGN_MANAGER",
        "domain": RoleDomain.operations,
        "description": "Dialer campaigns, lead routing, schedules & outbound lists.",
        "is_system": True,
    },
    {
        "name": "QA",
        "domain": RoleDomain.quality,
        "description": "Quality assurance audits, call evaluation & compliance scoring.",
        "is_system": True,
    },
    {
        "name": "VIEWER",
        "domain": RoleDomain.verification,
        "description": "Medicare verifiers, licensed call agents & customer verification.",
        "is_system": True,
    },
    {
        "name": "REPORTING_USER",
        "domain": RoleDomain.reporting,
        "description": "Call performance metrics, report generation & analytics access.",
        "is_system": True,
    },
]


async def seed_roles(db: AsyncSession) -> None:
    for seed in ROLE_SEED:
        result = await db.execute(select(Role).where(Role.name == seed["name"]))
        if result.scalar_one_or_none() is None:
            db.add(Role(**seed))
    await db.commit()

    await _migrate_legacy_roles(db)


async def _migrate_legacy_roles(db: AsyncSession) -> None:
    for old_name, new_name in LEGACY_ROLE_NAMES.items():
        legacy_result = await db.execute(
            select(Role).where(Role.name == old_name)
        )
        legacy_role = legacy_result.scalar_one_or_none()
        if legacy_role is None:
            continue

        spec_result = await db.execute(
            select(Role).where(Role.name == new_name)
        )
        spec_role = spec_result.scalar_one_or_none()
        if spec_role is None:
            continue

        # Merge junction rows: keep any already pointing at the spec role,
        # repoint the rest, then drop the legacy rows entirely.
        await db.execute(
            pg_insert(user_roles)
            .from_select(
                [user_roles.c.user_id, user_roles.c.role_id],
                select(user_roles.c.user_id, legacy_role.id).where(
                    user_roles.c.role_id == legacy_role.id
                ),
            )
            .on_conflict_do_nothing(index_elements=[user_roles.c.user_id, user_roles.c.role_id])
        )
        await db.execute(
            delete(user_roles).where(user_roles.c.role_id == legacy_role.id)
        )

        await db.execute(
            update(User)
            .where(User.role_id == legacy_role.id)
            .values(role_id=spec_role.id)
        )

        await db.execute(
            delete(Role).where(Role.id == legacy_role.id)
        )

    await db.commit()


async def seed_super_admin(db: AsyncSession) -> None:
    result = await db.execute(
        select(User).where(User.email == settings.seed_admin_email)
    )
    existing = result.scalar_one_or_none()

    role_result = await db.execute(select(Role).where(Role.name == "MASTER_ADMIN"))
    master_role = role_result.scalar_one_or_none()
    if master_role is None:
        return

    if existing is not None:
        needs_update = False
        if existing.status != UserStatus.APPROVED:
            existing.status = UserStatus.APPROVED
            needs_update = True
        if existing.role_id != master_role.id:
            existing.role_id = master_role.id
            needs_update = True

        has_junction = await db.execute(
            select(user_roles.c.role_id).where(
                user_roles.c.user_id == existing.id,
                user_roles.c.role_id == master_role.id,
            )
        )
        if has_junction.scalar_one_or_none() is None:
            await db.execute(
                user_roles.insert().values(user_id=existing.id, role_id=master_role.id)
            )
            needs_update = True

        if needs_update:
            await db.commit()
        return

    user = User(
        email=settings.seed_admin_email,
        hashed_password=hash_password(settings.seed_admin_password),
        full_name=settings.seed_admin_full_name,
        username="admin",
        extension="Not assigned",
        is_admin=True,
        is_active=True,
        status=UserStatus.APPROVED,
        role=master_role,
    )
    db.add(user)
    await db.flush()

    await db.execute(
        user_roles.insert().values(user_id=user.id, role_id=master_role.id)
    )
    await db.commit()


async def get_all_roles(db: AsyncSession) -> list[Role]:
    result = await db.execute(select(Role).order_by(Role.domain, Role.name))
    return list(result.scalars().all())


async def get_role_domains(db: AsyncSession) -> list[dict]:
    roles = await get_all_roles(db)
    grouped: dict[str, list[str]] = {}
    for role in roles:
        grouped.setdefault(role.domain.value, []).append(role.name)
    return [
        {"domain": domain, "roles": names} for domain, names in sorted(grouped.items())
    ]
