"""Audit jurnalini faqat so'nggi N kun (standart 3) saqlash.

Ilova ishga tushganda bir marta, keyin har soatda eski yozuvlar o'chiriladi.
Muddat `AUDIT_RETENTION_DAYS` muhit o'zgaruvchisi bilan o'zgartiriladi.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from sqlalchemy import delete

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.timeutils import utcnow
from app.models.models import AuditLog

logger = logging.getLogger(__name__)

PURGE_INTERVAL_SECONDS = 3600


async def purge_old_audit_logs() -> int:
    days = get_settings().audit_retention_days
    if days <= 0:
        return 0
    cutoff = utcnow() - timedelta(days=days)
    async with SessionLocal() as db:
        result = await db.execute(delete(AuditLog).where(AuditLog.created_at < cutoff))
        await db.commit()
    return result.rowcount or 0


async def retention_loop() -> None:
    while True:
        try:
            removed = await purge_old_audit_logs()
            if removed:
                logger.info("Audit jurnalidan %s ta eski yozuv o'chirildi", removed)
        except Exception:  # noqa: BLE001 — baza vaqtincha yo'q bo'lsa ham ilova ishlashda davom etsin
            logger.exception("Audit jurnalini tozalashda xato")
        await asyncio.sleep(PURGE_INTERVAL_SECONDS)
