from pydantic import BaseModel, Field

from app.models.enums import EmployeeKind, EmployeeStatus


class EmployeeUpdateRequest(BaseModel):
    kind: EmployeeKind | None = None
    status: EmployeeStatus | None = None
    position: str | None = None
    specialization: str | None = None
    education: str | None = None
    experience_years: int | None = Field(default=None, ge=0)
    office_id: str | None = None


class SetCommissionRequest(BaseModel):
    # Foizli model: 10/20/30 yoki SUPER_ADMIN xohlagan qiymat
    commission_percent: float = Field(ge=0, le=100)


class ScheduleItem(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: str  # "09:00"
    end_time: str  # "18:00"


class SetScheduleRequest(BaseModel):
    items: list[ScheduleItem]
