from __future__ import annotations

from pydantic import BaseModel

from app.core.pagination import PaginationQuery
from app.models.enums import CasePriority, CaseStatus, ServiceCategory


class CreateCaseRequest(BaseModel):
    title: str
    client_id: str
    description: str | None = None
    case_type: str | None = None
    category: ServiceCategory | None = None
    priority: CasePriority | None = None
    responsible_employee_id: str | None = None
    lawyer_id: str | None = None
    office_id: str | None = None


class UpdateCaseRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    case_type: str | None = None
    category: ServiceCategory | None = None
    status: CaseStatus | None = None
    priority: CasePriority | None = None
    responsible_employee_id: str | None = None
    lawyer_id: str | None = None


class CaseQuery(PaginationQuery):
    status: CaseStatus | None = None
    priority: CasePriority | None = None
    client_id: str | None = None
    responsible_employee_id: str | None = None


class CaseNoteRequest(BaseModel):
    body: str
