from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import NotificationChannel
from app.models.models import AuditLog, Notification
from app.modules.authentication.security_events import NOTIFY_USER_EVENTS, SecurityEvent
from app.modules.authentication.services.token_service import RequestMeta

logger = logging.getLogger("SecurityEvent")


def _describe(event: str, ctx: RequestMeta | None) -> str:
    where = f" (IP: {ctx.ip})" if ctx and ctx.ip else ""
    return {
        SecurityEvent.LOGIN: f"Hisobingizga yangi kirish amalga oshirildi{where}.",
        SecurityEvent.PASSWORD_CHANGE: "Parolingiz oʻzgartirildi.",
        SecurityEvent.PASSWORD_RESET: "Parolingiz tiklandi.",
        SecurityEvent.EMAIL_CHANGE: "Email manzilingiz oʻzgartirildi.",
        SecurityEvent.PHONE_CHANGE: "Telefon raqamingiz oʻzgartirildi.",
        SecurityEvent.ACCOUNT_LOCKED: "Hisobingiz koʻp muvaffaqiyatsiz urinishlar tufayli vaqtincha bloklandi.",
        SecurityEvent.SUSPICIOUS_ACTIVITY: f"Hisobingizda shubhali harakat aniqlandi{where}.",
    }.get(event, "Hisobingizda xavfsizlik hodisasi qayd etildi.")


async def record(
    db: AsyncSession,
    *,
    event: str,
    user_id: str | None = None,
    ctx: RequestMeta | None = None,
    meta: dict | None = None,
) -> None:
    """Xavfsizlik hodisasini audit_logs ga yozadi va zarur boʻlsa in-app bildirishnoma yaratadi.

    MUHIM: parol/token hech qachon yozilmaydi.
    """
    try:
        db.add(
            AuditLog(
                actor_id=user_id,
                action=event,
                entity="Auth",
                entity_id=user_id,
                after=meta or {},
                ip=ctx.ip if ctx else None,
                request_id=ctx.request_id if ctx else None,
            )
        )
        if user_id and event in NOTIFY_USER_EVENTS:
            db.add(
                Notification(
                    user_id=user_id,
                    channel=NotificationChannel.IN_APP,
                    title="Xavfsizlik ogohlantirishi",
                    body=_describe(event, ctx),
                )
            )
        await db.commit()
    except Exception:
        await db.rollback()
        logger.warning("Security event yozilmadi: %s", event)
