"""dashboard.service.js ekvivalenti."""

from __future__ import annotations

from datetime import datetime, timedelta
from app.core.timeutils import utcnow

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PaymentDirection, PaymentStatus
from app.models.models import Appointment, AuditLog, Case, Client, Employee, Payment, Task
from app.modules.dashboard.schemas import DashboardOverview

_ACTIVE_CASE_STATUSES = ["NEW", "OPEN", "IN_PROGRESS", "WAITING"]
_ACTIVE_TASK_STATUSES = ["TODO", "IN_PROGRESS", "OVERDUE"]


async def overview(db: AsyncSession) -> DashboardOverview:
    now = utcnow()
    soon = now + timedelta(days=7)
    one_day_ago = now - timedelta(days=1)

    clients = (
        await db.execute(select(func.count()).select_from(Client).where(Client.deleted_at.is_(None)))
    ).scalar_one()
    employees = (
        await db.execute(select(func.count()).select_from(Employee).where(Employee.deleted_at.is_(None)))
    ).scalar_one()
    active_cases = (
        await db.execute(
            select(func.count())
            .select_from(Case)
            .where(Case.deleted_at.is_(None), Case.status.in_(_ACTIVE_CASE_STATUSES))
        )
    ).scalar_one()
    appointments = (
        await db.execute(
            select(func.count())
            .select_from(Appointment)
            .where(
                Appointment.deleted_at.is_(None),
                Appointment.start_at >= now,
                Appointment.start_at <= soon,
            )
        )
    ).scalar_one()
    tasks = (
        await db.execute(
            select(func.count())
            .select_from(Task)
            .where(Task.deleted_at.is_(None), Task.status.in_(_ACTIVE_TASK_STATUSES))
        )
    ).scalar_one()
    payments = (
        await db.execute(select(func.count()).select_from(Payment).where(Payment.deleted_at.is_(None)))
    ).scalar_one()
    income = (
        await db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.deleted_at.is_(None),
                Payment.direction == PaymentDirection.INCOME,
                Payment.status == PaymentStatus.PAID,
            )
        )
    ).scalar()
    expense = (
        await db.execute(
            select(func.sum(Payment.amount)).where(
                Payment.deleted_at.is_(None),
                Payment.direction == PaymentDirection.EXPENSE,
                Payment.status == PaymentStatus.PAID,
            )
        )
    ).scalar()
    system_events = (
        await db.execute(select(func.count()).select_from(AuditLog).where(AuditLog.created_at >= one_day_ago))
    ).scalar_one()

    return DashboardOverview(
        clients=clients,
        employees=employees,
        active_cases=active_cases,
        appointments=appointments,
        tasks=tasks,
        payments=payments,
        income=float(income or 0),
        expense=float(expense or 0),
        system_events=system_events,
    )
