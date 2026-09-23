"""dashboard.service.js#overview() natija shakli ekvivalenti."""

from __future__ import annotations

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    clients: int
    employees: int
    active_cases: int
    appointments: int
    tasks: int
    payments: int
    income: float
    expense: float
    system_events: int
