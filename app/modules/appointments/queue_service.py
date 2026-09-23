"""appointments/queue.service.js ekvivalenti — jismoniy ofis navbat/talon
tizimi (QueueEntry). DIQQAT: bu BullMQ ish navbati (job queue) EMAS — bu
mutlaqo alohida domen, faqat asl loyihada bir xil `modules/appointments/`
papkasida yashagan."""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import QueueStatus
from app.models.models import QueueEntry


def _day_key(d: datetime) -> date_type:
    return date_type(d.year, d.month, d.day)


async def join(
    db: AsyncSession,
    *,
    assignee_id: str | None,
    client_id: str | None,
    office_id: str | None,
    appointment_id: str | None,
) -> QueueEntry:
    """Navbatga qo'shish — raqam ketma-ketligi advisory lock bilan himoyalangan."""
    today = _day_key(utcnow())

    # shu kun+mutaxassis bo'yicha raqam berishni ketma-ket qilamiz
    lock_key = f"{today.isoformat()}:{assignee_id or 'any'}"
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": lock_key})

    last = (
        await db.execute(
            select(QueueEntry.number)
            .where(QueueEntry.date == today, QueueEntry.assignee_id == assignee_id)
            .order_by(QueueEntry.number.desc())
        )
    ).scalars().first()
    number = (last or 0) + 1

    entry = QueueEntry(
        date=today,
        number=number,
        status=QueueStatus.WAITING,
        assignee_id=assignee_id,
        client_id=client_id,
        office_id=office_id,
        appointment_id=appointment_id,
    )
    db.add(entry)
    await db.commit()
    return entry


async def board(db: AsyncSession, date_str: str | None, assignee_id: str | None) -> dict[str, list[QueueEntry]]:
    """Kunlik navbat - statuslar bo'yicha guruhlangan."""
    day = _day_key(datetime.fromisoformat(date_str)) if date_str else _day_key(utcnow())
    stmt = select(QueueEntry).where(QueueEntry.date == day)
    if assignee_id:
        stmt = stmt.where(QueueEntry.assignee_id == assignee_id)
    stmt = stmt.order_by(QueueEntry.number.asc())
    entries = list((await db.execute(stmt)).scalars().all())

    columns = [
        QueueStatus.WAITING,
        QueueStatus.INVITED,
        QueueStatus.IN_SERVICE,
        QueueStatus.DONE,
        QueueStatus.CANCELLED,
    ]
    return {c.value: [e for e in entries if e.status == c] for c in columns}


async def update_status(db: AsyncSession, id: str, new_status: QueueStatus) -> QueueEntry:
    entry = (await db.execute(select(QueueEntry).where(QueueEntry.id == id))).scalar_one_or_none()
    if not entry:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Navbat yozuvi topilmadi")
    entry.status = new_status
    if new_status == QueueStatus.INVITED:
        entry.called_at = utcnow()
    await db.commit()
    return entry
