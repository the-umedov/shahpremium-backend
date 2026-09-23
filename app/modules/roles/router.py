from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.modules.roles import service
from app.modules.roles.schemas import CreateRoleRequest, UpdateRoleRequest

router = APIRouter(tags=["roles"])

_manage = Depends(require_permissions("roles.manage"))


@router.get("", dependencies=[_manage])
async def list_roles(db: DbSession) -> list[dict]:
    return await service.list_roles(db)


@router.post("", status_code=201, dependencies=[_manage])
async def create_role(dto: CreateRoleRequest, db: DbSession) -> dict:
    """Faqat `roles.manage` ruxsatiga ega foydalanuvchi (SUPER_ADMIN/ADMIN)
    yangi (tizim bo'lmagan) rol yaratishi mumkin."""
    return await service.create_role(db, dto)


@router.get("/{role_id}", dependencies=[_manage])
async def get_role(role_id: str, db: DbSession) -> dict:
    return await service.get_role(db, role_id)


@router.put("/{role_id}", dependencies=[_manage])
async def update_role(role_id: str, dto: UpdateRoleRequest, db: DbSession) -> dict:
    """Nomi/tavsifi va/yoki ruxsatlar ro'yxatini yangilaydi (tizim rollariga ham
    ruxsat tayinlash mumkin — faqat o'chirish/kalitni o'zgartirish bloklangan)."""
    return await service.update_role(db, role_id, dto)


@router.delete("/{role_id}", dependencies=[_manage])
async def delete_role(role_id: str, db: DbSession) -> dict:
    """Tizim roli (is_system=True) yoki foydalanuvchilarga biriktirilgan
    rolni o'chirib bo'lmaydi — xatolik qaytariladi."""
    await service.delete_role(db, role_id)
    return {"ok": True}
