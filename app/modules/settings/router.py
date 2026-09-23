from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.settings import service
from app.modules.settings.schemas import PreferenceUpdateRequest, SettingUpsertRequest

router = APIRouter(tags=["settings"])

# NOTE on route layout: original Nest app had two independent top-level controllers —
# SettingsController @Controller("settings") (guarded by "settings.manage") and
# PreferencesController @Controller("preferences") (no RequirePermissions — just the
# global JwtAuthGuard, i.e. self-service for any logged-in user). main.py here only
# mounts a single `settings_router` at f"{prefix}/settings", so preferences end up at
# f"{prefix}/settings/preferences" instead of the original's top-level f"{prefix}/preferences".


@router.get("", dependencies=[Depends(require_permissions("settings.manage"))])
async def list_settings(db: DbSession) -> list:
    return await service.list_settings(db)


@router.put("", dependencies=[Depends(require_permissions("settings.manage"))])
async def upsert_setting(dto: SettingUpsertRequest, db: DbSession):
    return await service.upsert_setting(db, dto)


# Foydalanuvchi shaxsiy sozlamalari (til, mavzu, timezone, sana formati, bildirishnomalar).
# Ruxsat talab qilinmaydi — faqat tizimga kirgan bo'lish kifoya (o'z-o'ziga xizmat).
@router.get("/preferences")
async def get_preferences(db: DbSession, user: CurrentUser):
    return await service.get_preferences(db, user)


@router.put("/preferences")
async def update_preferences(dto: PreferenceUpdateRequest, db: DbSession, user: CurrentUser):
    return await service.update_preferences(db, user, dto)
