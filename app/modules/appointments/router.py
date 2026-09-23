"""appointments.controller.js + queue.controller.js ekvivalenti.

DIQQAT: asl loyihada bular ikki alohida NestJS controller (`/appointments` va
`/queue`), lekin bir xil `modules/appointments/` papkasida yashagan. Bu yerda
ham xuddi shunday — `queue_router` shu modul ichida yaratiladi va asosiy
`router`ga qo'shiladi (`/appointments/queue/...` bo'lib chiqadi, chunki
`app/main.py` faqat `appointments_router`ni `/appointments` prefiksi bilan
ulaydi)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.models.models import Appointment, Employee, QueueEntry
from app.modules.appointments import queue_service, service
from app.modules.appointments.schemas import (
    AvailabilityQuery,
    BookAppointmentRequest,
    QueueJoinRequest,
    QueueUpdateStatusRequest,
    SpecialistsQuery,
    UpdateStatusRequest,
)

router = APIRouter(tags=["appointments"])

_manage = Depends(require_permissions("appointments.manage"))


def _serialize_appointment(a: Appointment) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        "start_at": a.start_at,
        "end_at": a.end_at,
        "location": a.location,
        "status": a.status,
        "assignee_id": a.assignee_id,
        "client_id": a.client_id,
        "case_id": a.case_id,
        "created_at": a.created_at,
        "updated_at": a.updated_at,
    }


def _serialize_specialist(emp: Employee) -> dict:
    user = emp.user
    return {
        "id": emp.id,
        "kind": emp.kind,
        "specialization": emp.specialization,
        "experience_years": emp.experience_years,
        "languages": emp.languages,
        "status": emp.status,
        "user": (
            {
                "id": user.id,
                "region": {"id": user.region.id, "name": user.region.name} if user.region else None,
                "profile": (
                    {"first_name": user.profile.first_name, "last_name": user.profile.last_name}
                    if user.profile
                    else None
                ),
            }
            if user
            else None
        ),
    }


def _serialize_specialist_detail(emp: Employee) -> dict:
    data = _serialize_specialist(emp)
    if emp.user is not None and data["user"] is not None:
        data["user"]["schedules"] = [
            {
                "id": s.id,
                "day_of_week": s.day_of_week,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "is_active": s.is_active,
            }
            for s in emp.user.schedules
        ]
    return data


def _serialize_queue_entry(e: QueueEntry) -> dict:
    return {
        "id": e.id,
        "date": e.date,
        "number": e.number,
        "status": e.status,
        "assignee_id": e.assignee_id,
        "client_id": e.client_id,
        "office_id": e.office_id,
        "appointment_id": e.appointment_id,
        "joined_at": e.joined_at,
        "called_at": e.called_at,
    }


@router.get("/specialists", dependencies=[_manage])
async def list_specialists(db: DbSession, query: SpecialistsQuery = Depends()) -> list[dict]:
    rows = await service.specialists(db, query)
    return [_serialize_specialist(r) for r in rows]


@router.get("/specialists/{id}", dependencies=[_manage])
async def get_specialist(id: str, db: DbSession) -> dict:
    emp = await service.specialist(db, id)
    return _serialize_specialist_detail(emp)


@router.get("/availability", dependencies=[_manage])
async def get_availability(db: DbSession, query: AvailabilityQuery = Depends()) -> dict:
    return await service.availability(db, query)


@router.get("/calendar", dependencies=[_manage])
async def get_calendar(
    db: DbSession,
    user: CurrentUser,
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    assignee_id: str | None = Query(None),
) -> list[dict]:
    rows = await service.calendar(db, from_, to, assignee_id, user)
    return [_serialize_appointment(r) for r in rows]


@router.post("", status_code=201, dependencies=[_manage])
async def book_appointment(dto: BookAppointmentRequest, db: DbSession, user: CurrentUser) -> dict:
    appt = await service.book(db, dto, user)
    return _serialize_appointment(appt)


@router.get("/{id}", dependencies=[_manage])
async def get_appointment(id: str, db: DbSession, user: CurrentUser) -> dict:
    appt = await service.get(db, id, user)
    return _serialize_appointment(appt)


@router.patch("/{id}/status", dependencies=[_manage])
async def update_appointment_status(id: str, dto: UpdateStatusRequest, db: DbSession, user: CurrentUser) -> dict:
    appt = await service.update_status(db, id, dto.status, user)
    return _serialize_appointment(appt)


# ======================================================================
# QUEUE (queue.controller.js) — ofis navbat/talon tizimi
# ======================================================================

queue_router = APIRouter(prefix="/queue", tags=["queue"])


@queue_router.get("/board", dependencies=[_manage])
async def queue_board(
    db: DbSession,
    date: str | None = Query(None),
    assignee_id: str | None = Query(None),
) -> dict:
    columns = await queue_service.board(db, date, assignee_id)
    return {k: [_serialize_queue_entry(e) for e in v] for k, v in columns.items()}


@queue_router.post("", status_code=201, dependencies=[_manage])
async def queue_join(dto: QueueJoinRequest, db: DbSession, user: CurrentUser) -> dict:
    client_id = user.client_id or dto.client_id
    entry = await queue_service.join(
        db,
        assignee_id=dto.assignee_id,
        client_id=client_id,
        office_id=dto.office_id,
        appointment_id=dto.appointment_id,
    )
    return _serialize_queue_entry(entry)


@queue_router.patch("/{id}/status", dependencies=[_manage])
async def queue_update_status(id: str, dto: QueueUpdateStatusRequest, db: DbSession) -> dict:
    entry = await queue_service.update_status(db, id, dto.status)
    return _serialize_queue_entry(entry)


router.include_router(queue_router)
