from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from app.core.security import AuthUser
from app.models.enums import RoleKey


class ObjectAccessService:
    """OBJECT-LEVEL ACCESS (object-access.ts ekvivalenti).

    Ruxsat (permission) — "shu turdagi resursni koʻrish mumkinmi?" degan savolga javob beradi.
    Object-level access — "AYNAN SHU yozuvni koʻrish mumkinmi?" degan savolga.
    Shu sababli har bir resurs uchun:
      1) list soʻrovlarda scope_by_client() ni `where` ga qoʻshamiz;
      2) bitta yozuv olinganda assert_client_ownership() bilan tegishlilikni tekshiramiz.
    """

    @staticmethod
    def has_role(user: AuthUser, *roles: RoleKey) -> bool:
        keys = {r.value for r in roles}
        return any(r in keys for r in user.roles)

    @classmethod
    def is_privileged(cls, user: AuthUser) -> bool:
        return cls.has_role(user, RoleKey.SUPER_ADMIN, RoleKey.ADMIN)

    @classmethod
    def is_client(cls, user: AuthUser) -> bool:
        return cls.has_role(user, RoleKey.CLIENT)

    @classmethod
    def scope_by_client(cls, user: AuthUser) -> dict[str, Any]:
        """SUPER_ADMIN/ADMIN: cheklovsiz; CLIENT: faqat oʻz client_id;
        xodim/advokat: oʻz ofisi doirasida (case orqali)."""
        if cls.is_privileged(user):
            return {}
        if cls.is_client(user):
            if not user.client_id:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Mijoz profili topilmadi")
            return {"client_id": user.client_id}
        if user.office_id:
            return {"case": {"office_id": user.office_id}}
        return {}

    @classmethod
    def assert_client_ownership(cls, user: AuthUser, record: Any) -> None:
        """`record` topilmasa yoki tegishli boʻlmasa — 404 (mavjudligini oshkor qilmaslik uchun)."""
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
        if cls.is_privileged(user):
            return
        if cls.is_client(user):
            if getattr(record, "client_id", None) != user.client_id:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
            return
        record_office_id = getattr(record, "office_id", None)
        if user.office_id and record_office_id and record_office_id != user.office_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")


object_access = ObjectAccessService()
