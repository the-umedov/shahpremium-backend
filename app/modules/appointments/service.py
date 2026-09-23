"""appointments.service.js ekvivalenti.

Uchrashuvlarni rejalashtirish: mutaxassislarni topish (specialists), kunlik
bo'sh vaqt oralig'ini hisoblash (availability — ish jadvali - bandlik -
ta'til), bron qilish (advisory lock bilan poyga holatidan himoyalangan) va
kalendar/holat yangilash.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import AuthUser
from app.models.enums import (
    AppointmentStatus,
    EmployeeKind,
    EmployeeStatus,
    NotificationChannel,
    RoleKey,
)
from app.models.models import (
    Appointment,
    Client,
    Employee,
    Notification,
    Schedule,
    TimeOff,
    User,
    UserProfile,
)
from app.modules.appointments.schemas import (
    AvailabilityQuery,
    BookAppointmentRequest,
    SpecialistsQuery,
)

# Bandlikda hisobga olinadigan (bo'sh emas) statuslar
ACTIVE_STATUSES = [
    AppointmentStatus.SCHEDULED,
    AppointmentStatus.PENDING,
    AppointmentStatus.CONFIRMED,
    AppointmentStatus.IN_PROGRESS,
]


def is_client(user: AuthUser) -> bool:
    return RoleKey.CLIENT.value in user.roles


def privileged(user: AuthUser) -> bool:
    privileged_roles = {RoleKey.SUPER_ADMIN.value, RoleKey.ADMIN.value, RoleKey.MANAGER.value}
    return any(r in privileged_roles for r in user.roles)


async def specialists(db: AsyncSession, query: SpecialistsQuery) -> list[Employee]:
    """1-3: mutaxassislarni tur + region bo'yicha topish."""
    kinds = [query.kind] if query.kind else [EmployeeKind.LAWYER, EmployeeKind.ADVOCATE]
    stmt = (
        select(Employee)
        .options(
            selectinload(Employee.user).selectinload(User.region),
            selectinload(Employee.user).selectinload(User.profile),
        )
        .where(
            Employee.deleted_at.is_(None),
            Employee.status == EmployeeStatus.ACTIVE,
            Employee.kind.in_(kinds),
        )
    )
    if query.region_id or query.search:
        stmt = stmt.join(Employee.user)
    if query.region_id:
        stmt = stmt.where(User.region_id == query.region_id)
    if query.search:
        stmt = stmt.join(User.profile).where(
            or_(
                UserProfile.first_name.ilike(f"%{query.search}%"),
                UserProfile.last_name.ilike(f"%{query.search}%"),
            )
        )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def specialist(db: AsyncSession, id: str) -> Employee:
    """4-5: mutaxassis profili."""
    stmt = (
        select(Employee)
        .options(
            selectinload(Employee.user).selectinload(User.profile),
            selectinload(Employee.user).selectinload(User.region),
            selectinload(Employee.user).selectinload(User.schedules),
        )
        .where(Employee.id == id, Employee.deleted_at.is_(None))
    )
    emp = (await db.execute(stmt)).scalar_one_or_none()
    if not emp:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mutaxassis topilmadi")
    return emp


async def availability(db: AsyncSession, query: AvailabilityQuery) -> dict:
    """6-7: kun bo'yicha bo'sh oraliqlar (ish soatlari - bandlik - ta'til)."""
    day = datetime.fromisoformat(query.date)
    day_start = datetime(day.year, day.month, day.day)  # naive — DB ustuni ham naive
    day_end = day_start + timedelta(days=1)
    # JS Date#getUTCDay(): 0=Yakshanba..6=Shanba; Python weekday(): 0=Dushanba..6=Yakshanba
    dow = (day_start.weekday() + 1) % 7

    schedule = (
        await db.execute(
            select(Schedule).where(
                Schedule.user_id == query.assignee_id,
                Schedule.day_of_week == dow,
                Schedule.is_active.is_(True),
            )
        )
    ).scalars().first()
    if not schedule:
        return {"working_hours": None, "busy": [], "slots": []}

    busy = (
        await db.execute(
            select(Appointment.start_at, Appointment.end_at)
            .where(
                Appointment.assignee_id == query.assignee_id,
                Appointment.deleted_at.is_(None),
                Appointment.status.in_(ACTIVE_STATUSES),
                Appointment.start_at < day_end,
                Appointment.end_at > day_start,
            )
            .order_by(Appointment.start_at.asc())
        )
    ).all()
    time_off = (
        await db.execute(
            select(TimeOff.start_at, TimeOff.end_at).where(
                TimeOff.user_id == query.assignee_id,
                TimeOff.start_at < day_end,
                TimeOff.end_at > day_start,
            )
        )
    ).all()

    # 30 daqiqalik slotlar
    sh, sm = (int(x) for x in schedule.start_time.split(":"))
    eh, em = (int(x) for x in schedule.end_time.split(":"))
    slot_delta = timedelta(minutes=30)
    work_start = day_start + timedelta(hours=sh, minutes=sm)
    work_end = day_start + timedelta(hours=eh, minutes=em)

    blocked = [(b.start_at, b.end_at) for b in busy] + [(t.start_at, t.end_at) for t in time_off]

    slots: list[dict] = []
    t = work_start
    while t + slot_delta <= work_end:
        s, e = t, t + slot_delta
        overlap = any(b_start < e and b_end > s for b_start, b_end in blocked)
        if not overlap:
            slots.append({"start_at": s.isoformat(), "end_at": e.isoformat()})
        t += slot_delta

    return {
        "working_hours": {"start": schedule.start_time, "end": schedule.end_time},
        "busy": [{"start_at": b.start_at.isoformat(), "end_at": b.end_at.isoformat()} for b in busy],
        "slots": slots,
    }


async def book(db: AsyncSession, dto: BookAppointmentRequest, user: AuthUser) -> Appointment:
    """8-9: bron - konflikt tekshiruvi + race-condition himoyasi (advisory lock)."""
    start, end = dto.start_at, dto.end_at
    if not start < end:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Boshlanish tugashdan oldin bo'lishi kerak")

    client_id = user.client_id if is_client(user) else dto.client_id

    # Shu mutaxassis uchun bronlashni ketma-ket qilamiz (race-condition himoyasi)
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": dto.assignee_id})

    conflict = (
        await db.execute(
            select(func.count())
            .select_from(Appointment)
            .where(
                Appointment.assignee_id == dto.assignee_id,
                Appointment.deleted_at.is_(None),
                Appointment.status.in_(ACTIVE_STATUSES),
                Appointment.start_at < end,
                Appointment.end_at > start,
            )
        )
    ).scalar_one()
    if conflict > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bu vaqt band — boshqa vaqt tanlang")

    appt = Appointment(
        title=dto.title,
        start_at=start,
        end_at=end,
        location=dto.location,
        status=AppointmentStatus.PENDING,
        assignee_id=dto.assignee_id,
        client_id=client_id,
        case_id=dto.case_id,
    )
    db.add(appt)
    await db.flush()

    # Mutaxassisga bildirishnoma
    db.add(
        Notification(
            user_id=dto.assignee_id,
            channel=NotificationChannel.IN_APP,
            title="Yangi uchrashuv so'rovi",
            body=f"{dto.title} — {start.isoformat()}",
        )
    )
    await db.commit()
    return appt


async def calendar(
    db: AsyncSession,
    from_: datetime,
    to: datetime,
    assignee_id: str | None,
    user: AuthUser,
) -> list[Appointment]:
    """Kalendar: oraliqdagi uchrashuvlar (kun/hafta/oy/list uchun)."""
    stmt = select(Appointment).where(
        Appointment.deleted_at.is_(None),
        Appointment.start_at < to,
        Appointment.end_at > from_,
    )
    if assignee_id:
        stmt = stmt.where(Appointment.assignee_id == assignee_id)
    elif is_client(user):
        stmt = stmt.where(Appointment.client_id == (user.client_id or "__none__"))
    elif not privileged(user):
        stmt = stmt.where(Appointment.assignee_id == user.id)
    stmt = stmt.order_by(Appointment.start_at.asc())
    return list((await db.execute(stmt)).scalars().all())


async def get(db: AsyncSession, id: str, user: AuthUser) -> Appointment:
    appt = (
        await db.execute(select(Appointment).where(Appointment.id == id, Appointment.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if not appt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Uchrashuv topilmadi")
    # object-level: mijoz faqat o'zinikini
    if is_client(user) and appt.client_id != user.client_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Uchrashuv topilmadi")
    return appt


async def update_status(db: AsyncSession, id: str, new_status: AppointmentStatus, user: AuthUser) -> Appointment:
    appt = await get(db, id, user)
    appt.status = new_status
    await db.flush()

    # mijozga xabar (tasdiq/bekor)
    if appt.client_id:
        client = (
            await db.execute(select(Client).where(Client.id == appt.client_id))
        ).scalar_one_or_none()
        if client and client.user_id:
            db.add(
                Notification(
                    user_id=client.user_id,
                    channel=NotificationChannel.IN_APP,
                    title="Uchrashuv holati o'zgardi",
                    body=f"Holat: {new_status.value}",
                )
            )
    await db.commit()
    return appt
