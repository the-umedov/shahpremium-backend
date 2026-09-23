from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.core.pagination import PaginationQuery
from app.models.enums import ClientType


class CreateClientRequest(BaseModel):
    full_name: str
    client_type: ClientType | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_id: str | None = None
    region_id: str | None = None
    responsible_employee_id: str | None = None


class UpdateClientRequest(BaseModel):
    full_name: str | None = None
    client_type: ClientType | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_id: str | None = None
    region_id: str | None = None
    responsible_employee_id: str | None = None


class ClientQuery(PaginationQuery):
    region_id: str | None = None
    responsible_employee_id: str | None = None


class TimelineNoteRequest(BaseModel):
    title: str
    description: str | None = None
