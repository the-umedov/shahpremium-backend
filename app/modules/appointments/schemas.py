"""appointments.dto + queue DTO (queue.controller.js o'zining alohida DTO
klassiga ega emas — controller to'g'ridan-to'g'ri `Object` sifatida body qabul
qiladi) ekvivalenti."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import AppointmentStatus, EmployeeKind, QueueStatus


class SpecialistsQuery(BaseModel):
    kind: EmployeeKind | None = None
    region_id: str | None = None
    search: str | None = None


class AvailabilityQuery(BaseModel):
    assignee_id: str  # mutaxassis User.id
    date: str  # YYYY-MM-DD


class BookAppointmentRequest(BaseModel):
    assignee_id: str  # mutaxassis User.id
    title: str
    start_at: datetime
    end_at: datetime
    location: str | None = None
    case_id: str | None = None
    client_id: str | None = None


class UpdateStatusRequest(BaseModel):
    status: AppointmentStatus


class QueueJoinRequest(BaseModel):
    assignee_id: str | None = None
    client_id: str | None = None
    office_id: str | None = None
    appointment_id: str | None = None


class QueueUpdateStatusRequest(BaseModel):
    status: QueueStatus
