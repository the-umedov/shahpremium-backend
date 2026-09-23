from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.pagination import PaginationQuery
from app.models.enums import ContractStatus


class CreateContractRequest(BaseModel):
    client_id: str
    case_id: str | None = None
    responsible_employee_id: str | None = None
    amount: float | None = Field(default=None, ge=0)
    currency: str | None = None
    commission_percent: float | None = Field(default=None, ge=0)
    start_date: str | None = None
    end_date: str | None = None


class UpdateContractRequest(BaseModel):
    status: ContractStatus | None = None
    amount: float | None = Field(default=None, ge=0)
    currency: str | None = None
    commission_percent: float | None = Field(default=None, ge=0)
    start_date: str | None = None
    end_date: str | None = None
    responsible_employee_id: str | None = None


class ContractQuery(PaginationQuery):
    status: ContractStatus | None = None
    client_id: str | None = None
