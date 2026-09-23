"""employees.service.js ekvivalenti."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import PaginationQuery, build_page, to_paginated
from app.core.rbac import object_access
from app.core.security import AuthUser
from app.models.enums import EmployeeKind, EmployeeStatus, PaymentStatus, RoleKey
from app.models.models import (
    Advocate,
    Case,
    Client,
    Contract,
    Employee,
    Lawyer,
    Office,
    Payment,
    Schedule,
    Task,
    User,
    UserProfile,
)
from app.modules.employees.schemas import (
    EmployeeUpdateRequest,
    ScheduleItem,
)


def _serialize(employee: Employee, office: Office | None) -> dict:
    user = employee.user
    return {
        "id": employee.id,
        "user_id": employee.user_id,
        "office_id": employee.office_id,
        "kind": employee.kind,
        "status": employee.status,
        "position": employee.position,
        "specialization": employee.specialization,
        "education": employee.education,
        "experience_years": employee.experience_years,
        "commission_percent": employee.commission_percent,
        "languages": employee.languages,
        "hire_date": employee.hire_date,
        "created_at": employee.created_at,
        "updated_at": employee.updated_at,
        "office": {"id": office.id, "name": office.name} if office else None,
        "user": (
            {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "is_active": user.is_active,
                "region": {"id": user.region.id, "name": user.region.name} if user.region else None,
                "profile": (
                    {"first_name": user.profile.first_name, "last_name": user.profile.last_name}
                    if user.profile
                    else None
                ),
                "schedules": [
                    {
                        "id": s.id,
                        "day_of_week": s.day_of_week,
                        "start_time": s.start_time,
                        "end_time": s.end_time,
                        "is_active": s.is_active,
                    }
                    for s in user.schedules
                ],
            }
            if user
            else None
        ),
    }


def _base_stmt():
    # Employee modelida `office` relationship yo'q (faqat office_id FK) — shu sababli
    # Office bilan qo'lda outerjoin qilinadi.
    return (
        select(Employee, Office)
        .join(User, Employee.user_id == User.id)
        .outerjoin(Office, Employee.office_id == Office.id)
        .outerjoin(UserProfile, UserProfile.user_id == User.id)
        .options(
            selectinload(Employee.user).selectinload(User.profile),
            selectinload(Employee.user).selectinload(User.region),
            selectinload(Employee.user).selectinload(User.schedules),
        )
    )


async def list_employees(
    db: AsyncSession,
    query: PaginationQuery,
    kind: EmployeeKind | None,
    emp_status: EmployeeStatus | None,
    region_id: str | None,
) -> dict:
    page_info = build_page(query, default_sort="created_at")

    stmt = _base_stmt().where(Employee.deleted_at.is_(None))
    count_stmt = (
        select(func.count(Employee.id))
        .join(User, Employee.user_id == User.id)
        .outerjoin(UserProfile, UserProfile.user_id == User.id)
        .where(Employee.deleted_at.is_(None))
    )
    if kind:
        stmt = stmt.where(Employee.kind == kind)
        count_stmt = count_stmt.where(Employee.kind == kind)
    if emp_status:
        stmt = stmt.where(Employee.status == emp_status)
        count_stmt = count_stmt.where(Employee.status == emp_status)
    if region_id:
        stmt = stmt.where(User.region_id == region_id)
        count_stmt = count_stmt.where(User.region_id == region_id)
    if query.search:
        clause = or_(
            UserProfile.first_name.ilike(f"%{query.search}%"),
            UserProfile.last_name.ilike(f"%{query.search}%"),
        )
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = (await db.execute(count_stmt)).scalar_one()
    sort_col = getattr(Employee, page_info["sort"], Employee.created_at)
    order_col = sort_col.desc() if page_info["order"] == "desc" else sort_col.asc()
    rows = (
        await db.execute(stmt.order_by(order_col).offset(page_info["skip"]).limit(page_info["take"]))
    ).all()

    items = [_serialize(employee, office) for employee, office in rows]
    return to_paginated(items, total, page_info["page"], page_info["limit"])


async def _get_raw(db: AsyncSession, employee_id: str) -> Employee:
    """employees.service.js#getRaw ekvivalenti."""
    employee = (
        await db.execute(
            select(Employee).where(Employee.id == employee_id, Employee.deleted_at.is_(None))
        )
    ).scalar_one_or_none()
    if employee is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Xodim topilmadi")
    return employee


async def _compute_stats(db: AsyncSession, employee_id: str, user_id: str, commission_percent: Decimal) -> dict:
    """employees.service.js#computeStats ekvivalenti."""
    clients = (
        await db.execute(
            select(func.count()).select_from(Client).where(
                Client.responsible_employee_id == employee_id, Client.deleted_at.is_(None)
            )
        )
    ).scalar_one()

    # asStaff: OR({ lawyer: { userId } }, { advocate: { userId } })
    as_staff_case_ids = (
        select(Case.id)
        .outerjoin(Lawyer, Case.lawyer_id == Lawyer.id)
        .outerjoin(Advocate, Case.advocate_id == Advocate.id)
        .where(or_(Lawyer.user_id == user_id, Advocate.user_id == user_id))
    )

    cases = (
        await db.execute(
            select(func.count()).select_from(Case).where(
                Case.id.in_(as_staff_case_ids), Case.deleted_at.is_(None)
            )
        )
    ).scalar_one()

    contracts = (
        await db.execute(
            select(func.count()).select_from(Contract).where(
                Contract.case_id.in_(as_staff_case_ids), Contract.deleted_at.is_(None)
            )
        )
    ).scalar_one()

    tasks = (
        await db.execute(
            select(func.count()).select_from(Task).where(
                Task.assignee_id == user_id, Task.deleted_at.is_(None)
            )
        )
    ).scalar_one()

    paid_sum = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PaymentStatus.PAID, Payment.case_id.in_(as_staff_case_ids)
            )
        )
    ).scalar_one()

    total_revenue = float(paid_sum)
    commission_percent_f = float(commission_percent)
    return {
        "clients": clients,
        "cases": cases,
        "contracts": contracts,
        "tasks": tasks,
        "total_revenue": total_revenue,
        "commission_percent": commission_percent_f,
        "commission_earned": round(total_revenue * commission_percent_f / 100),
    }


async def get_employee(db: AsyncSession, employee_id: str) -> dict:
    """Xodim kartasi — profil + statistika + moliyaviy koʻrsatkichlar."""
    row = (
        await db.execute(
            _base_stmt().where(Employee.id == employee_id, Employee.deleted_at.is_(None))
        )
    ).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Xodim topilmadi")
    employee, office = row
    stats = await _compute_stats(db, employee.id, employee.user_id, employee.commission_percent)
    result = _serialize(employee, office)
    result["stats"] = stats
    return result


async def update_employee(db: AsyncSession, employee_id: str, dto: EmployeeUpdateRequest) -> dict:
    employee = await _get_raw(db, employee_id)
    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    await db.commit()
    return await get_employee(db, employee_id)


async def set_commission(db: AsyncSession, employee_id: str, percent: float, user: AuthUser) -> dict:
    """Foizli modelni faqat SUPER_ADMIN sozlaydi."""
    if not object_access.has_role(user, RoleKey.SUPER_ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat SUPER_ADMIN foizni sozlashi mumkin")
    employee = await _get_raw(db, employee_id)
    employee.commission_percent = Decimal(str(percent))
    await db.commit()
    return await get_employee(db, employee_id)


async def set_schedule(db: AsyncSession, employee_id: str, items: list[ScheduleItem]) -> list[dict]:
    """Ish grafigi (haftalik) — transaksion qayta oʻrnatish."""
    employee = await _get_raw(db, employee_id)
    await db.execute(delete(Schedule).where(Schedule.user_id == employee.user_id))
    for item in items:
        db.add(
            Schedule(
                user_id=employee.user_id,
                day_of_week=item.day_of_week,
                start_time=item.start_time,
                end_time=item.end_time,
            )
        )
    await db.commit()
    rows = (
        await db.execute(
            select(Schedule).where(Schedule.user_id == employee.user_id).order_by(Schedule.day_of_week.asc())
        )
    ).scalars().all()
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "day_of_week": s.day_of_week,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "is_active": s.is_active,
        }
        for s in rows
    ]
