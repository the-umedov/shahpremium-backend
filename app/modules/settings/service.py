from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthUser
from app.models.models import Setting, UserPreference
from app.modules.settings.schemas import PreferenceUpdateRequest, SettingUpsertRequest

# ---- settings.controller.js: global key/value sozlamalar ----


async def list_settings(db: AsyncSession) -> list[Setting]:
    rows = (await db.execute(select(Setting).order_by(Setting.key.asc()))).scalars().all()
    return list(rows)


async def upsert_setting(db: AsyncSession, dto: SettingUpsertRequest) -> Setting:
    existing = (await db.execute(select(Setting).where(Setting.key == dto.key))).scalar_one_or_none()
    if existing:
        existing.value = dto.value
        existing.scope = dto.scope or existing.scope
        setting = existing
    else:
        setting = Setting(key=dto.key, value=dto.value, scope=dto.scope or "GLOBAL")
        db.add(setting)
    await db.commit()
    return setting


# ---- preferences.controller.js: foydalanuvchi shaxsiy sozlamalari (o'z-o'ziga xizmat) ----

_DEFAULT_PREFERENCE = {
    "locale": "uz",
    "theme": "system",
    "timezone": "Asia/Tashkent",
    "date_format": "dd.MM.yyyy",
    "notify_in_app": True,
    "notify_email": True,
    "notify_sms": False,
    "notify_push": False,
}


async def get_preferences(db: AsyncSession, user: AuthUser) -> UserPreference | dict:
    pref = (await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))).scalar_one_or_none()
    return pref if pref is not None else dict(_DEFAULT_PREFERENCE)


async def update_preferences(db: AsyncSession, user: AuthUser, dto: PreferenceUpdateRequest) -> UserPreference:
    data = dto.model_dump(exclude_unset=True)
    pref = (await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))).scalar_one_or_none()
    if pref:
        for field, value in data.items():
            setattr(pref, field, value)
    else:
        pref = UserPreference(user_id=user.id, **data)
        db.add(pref)
    await db.commit()
    return pref
