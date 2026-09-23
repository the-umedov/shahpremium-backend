from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Permission, Role, RolePermission
from app.modules.roles.schemas import CreateRoleRequest, UpdateRoleRequest


def _serialize(r: Role) -> dict:
    return {
        "id": r.id,
        "key": r.key,
        "name": r.name,
        "description": r.description,
        "is_system": r.is_system,
        "count": {"users": len(r.users), "permissions": len(r.permissions)},
        "permissions": [{"id": rp.permission.id, "key": rp.permission.key} for rp in r.permissions],
    }


async def list_roles(db: AsyncSession) -> list[dict]:
    rows = (
        await db.execute(
            select(Role)
            .options(
                selectinload(Role.users),
                selectinload(Role.permissions).selectinload(RolePermission.permission),
            )
            .order_by(Role.key.asc())
        )
    ).scalars().all()
    return [_serialize(r) for r in rows]


async def _get_role(db: AsyncSession, role_id: str) -> Role:
    role = (
        await db.execute(
            select(Role)
            .options(
                selectinload(Role.users),
                selectinload(Role.permissions).selectinload(RolePermission.permission),
            )
            .where(Role.id == role_id)
        )
    ).scalar_one_or_none()
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rol topilmadi")
    return role


async def _set_permissions(db: AsyncSession, role: Role, permission_ids: list[str]) -> None:
    unique_ids = set(permission_ids)
    if unique_ids:
        count = (
            await db.execute(select(func.count()).select_from(Permission).where(Permission.id.in_(unique_ids)))
        ).scalar_one()
        if count != len(unique_ids):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Noto'g'ri ruxsat ID(lar)i")
    await db.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
    for pid in unique_ids:
        db.add(RolePermission(role_id=role.id, permission_id=pid))


async def create_role(db: AsyncSession, dto: CreateRoleRequest) -> dict:
    existing = (await db.execute(select(Role.id).where(Role.key == dto.key))).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bunday kalitli rol allaqachon mavjud")
    role = Role(key=dto.key, name=dto.name, description=dto.description, is_system=False)
    db.add(role)
    await db.flush()
    await _set_permissions(db, role, dto.permission_ids)
    await db.commit()
    return await get_role(db, role.id)


async def get_role(db: AsyncSession, role_id: str) -> dict:
    return _serialize(await _get_role(db, role_id))


async def update_role(db: AsyncSession, role_id: str, dto: UpdateRoleRequest) -> dict:
    role = await _get_role(db, role_id)
    if dto.name is not None:
        role.name = dto.name
    if dto.description is not None:
        role.description = dto.description
    if dto.permission_ids is not None:
        await _set_permissions(db, role, dto.permission_ids)
    await db.commit()
    return await get_role(db, role_id)


async def delete_role(db: AsyncSession, role_id: str) -> None:
    role = await _get_role(db, role_id)
    if role.is_system:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tizim rolini o'chirib bo'lmaydi")
    if role.users:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Bu rolga biriktirilgan foydalanuvchilar bor — avval ularni boshqa rolga o'tkazing",
        )
    await db.delete(role)
    await db.commit()
