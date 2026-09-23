from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from app.core.timeutils import utcnow

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import LoginAttempt, User

MAX_FAILED = 5
WINDOW = timedelta(minutes=15)
LOCK_DURATION = timedelta(minutes=15)


@dataclass
class AttemptParams:
    identifier: str
    ip: str | None
    user_agent: str | None
    success: bool


async def record_attempt(db: AsyncSession, params: AttemptParams) -> None:
    db.add(
        LoginAttempt(
            identifier=params.identifier,
            ip=params.ip,
            user_agent=params.user_agent,
            success=params.success,
        )
    )
    await db.commit()


async def recent_failures(db: AsyncSession, identifier: str, ip: str | None) -> int:
    """Identifikator yoki IP boʻyicha yaqin muvaffaqiyatsiz urinishlar soni."""
    since = utcnow() - WINDOW
    conditions = [LoginAttempt.identifier == identifier]
    if ip:
        conditions.append(LoginAttempt.ip == ip)
    result = await db.execute(
        select(func.count()).select_from(LoginAttempt).where(
            LoginAttempt.success.is_(False),
            LoginAttempt.created_at >= since,
            or_(*conditions),
        )
    )
    return result.scalar_one()


def is_locked(user: User) -> bool:
    return bool(user.locked_until) and user.locked_until > utcnow()


async def register_failure(db: AsyncSession, user_id: str) -> dict:
    """Muvaffaqiyatsiz urinish hisobini oshiradi; chegaradan oshsa bloklaydi."""
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    user.failed_login_count += 1
    locked = user.failed_login_count >= MAX_FAILED
    if locked:
        user.locked_until = utcnow() + LOCK_DURATION
    await db.commit()
    return {"locked": locked}


async def reset(db: AsyncSession, user_id: str) -> None:
    """Muvaffaqiyatli kirishda hisoblagichni tozalaydi."""
    await db.execute(
        update(User).where(User.id == user_id).values(failed_login_count=0, locked_until=None)
    )
    await db.commit()
