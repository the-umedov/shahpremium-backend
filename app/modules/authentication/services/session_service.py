from datetime import datetime
from app.core.timeutils import utcnow

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import RefreshToken


async def list_active(db: AsyncSession, user_id: str, current_session_id: str | None) -> list[dict]:
    """Foydalanuvchining faol (bekor qilinmagan, muddati oʻtmagan) sessiyalari."""
    rows = (
        await db.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > utcnow(),
            )
            .order_by(RefreshToken.last_used_at.desc())
        )
    ).scalars().all()
    return [
        {
            "id": r.id,
            "ip": r.ip,
            "user_agent": r.user_agent,
            "label": r.label,
            "last_used_at": r.last_used_at,
            "created_at": r.created_at,
            "current": r.id == current_session_id,
        }
        for r in rows
    ]
