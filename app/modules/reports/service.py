"""reports.service.js ekvivalenti."""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import PaymentDirection, PaymentStatus
from app.models.models import (
    Advocate,
    Case,
    CaseService,
    Client,
    Employee,
    Invoice,
    Lawyer,
    Payment,
    Service,
    User,
    UserProfile,
)
from app.modules.reports.schemas import ReportColumn, ReportData, ReportQuery


def _n(value) -> float:
    return float(value or 0)


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _date_where(f: ReportQuery) -> tuple:
    conditions = []
    if f.date_from:
        conditions.append(Payment.created_at >= _parse_date(f.date_from))
    if f.date_to:
        conditions.append(Payment.created_at <= _parse_date(f.date_to))
    return tuple(conditions)


def _payment_where(f: ReportQuery) -> list:
    conditions = [Payment.deleted_at.is_(None)]
    if f.client_id:
        conditions.append(Payment.client_id == f.client_id)
    conditions.extend(_date_where(f))
    return conditions


async def generate(db: AsyncSession, report_type: str, f: ReportQuery) -> ReportData:
    if report_type == "payments":
        return await _payments(db, f)
    if report_type == "income":
        return await _direction(db, f, PaymentDirection.INCOME, "Daromad hisoboti")
    if report_type == "expense":
        return await _direction(db, f, PaymentDirection.EXPENSE, "Xarajat hisoboti")
    if report_type == "debt":
        return await _debt(db, f)
    if report_type == "clients":
        return await _clients(db, f)
    if report_type == "employees":
        return await _employees(db, f)
    if report_type == "services":
        return await _services(db, f)
    if report_type == "cases":
        return await _cases(db, f)
    raise HTTPException(status.HTTP_400_BAD_REQUEST, "Noma'lum hisobot turi")


async def _payments(db: AsyncSession, f: ReportQuery) -> ReportData:
    stmt = (
        select(Payment)
        .options(selectinload(Payment.client))
        .where(*_payment_where(f))
        .order_by(Payment.created_at.desc())
        .limit(5000)
    )
    rows = (await db.execute(stmt)).scalars().all()
    return ReportData(
        title="Tolovlar hisoboti",
        columns=[
            ReportColumn(key="date", header="Sana"),
            ReportColumn(key="client", header="Mijoz"),
            ReportColumn(key="direction", header="Turi"),
            ReportColumn(key="category", header="Kategoriya"),
            ReportColumn(key="amount", header="Summa"),
            ReportColumn(key="currency", header="Valyuta"),
            ReportColumn(key="status", header="Holat"),
        ],
        rows=[
            {
                "date": p.created_at.date().isoformat(),
                "client": p.client.full_name if p.client else "-",
                "direction": p.direction,
                "category": p.category,
                "amount": _n(p.amount),
                "currency": p.currency,
                "status": p.status,
            }
            for p in rows
        ],
    )


async def _direction(db: AsyncSession, f: ReportQuery, direction: PaymentDirection, title: str) -> ReportData:
    stmt = (
        select(Payment.category, func.sum(Payment.amount), func.count())
        .where(*_payment_where(f), Payment.direction == direction, Payment.status == PaymentStatus.PAID)
        .group_by(Payment.category)
    )
    rows = (await db.execute(stmt)).all()
    return ReportData(
        title=title,
        columns=[
            ReportColumn(key="category", header="Kategoriya"),
            ReportColumn(key="count", header="Soni"),
            ReportColumn(key="total", header="Jami"),
        ],
        rows=[{"category": category, "count": count, "total": _n(total)} for category, total, count in rows],
    )


async def _debt(db: AsyncSession, f: ReportQuery) -> ReportData:
    invoiced_subq = (
        select(Invoice.client_id.label("client_id"), func.sum(Invoice.amount).label("invoiced"))
        .where(Invoice.deleted_at.is_(None))
        .group_by(Invoice.client_id)
        .subquery()
    )
    paid_subq = (
        select(Payment.client_id.label("client_id"), func.sum(Payment.amount).label("paid"))
        .where(
            Payment.deleted_at.is_(None),
            Payment.direction == PaymentDirection.INCOME,
            Payment.status == PaymentStatus.PAID,
        )
        .group_by(Payment.client_id)
        .subquery()
    )
    stmt = (
        select(Client.full_name, invoiced_subq.c.invoiced, paid_subq.c.paid)
        .select_from(Client)
        .outerjoin(invoiced_subq, invoiced_subq.c.client_id == Client.id)
        .outerjoin(paid_subq, paid_subq.c.client_id == Client.id)
        .where(Client.deleted_at.is_(None))
    )
    if f.region_id:
        stmt = stmt.where(Client.region_id == f.region_id)

    rows = []
    for full_name, invoiced, paid in (await db.execute(stmt)).all():
        invoiced_v = _n(invoiced)
        paid_v = _n(paid)
        debt = max(0.0, invoiced_v - paid_v)
        if debt > 0:
            rows.append({"client": full_name, "invoiced": invoiced_v, "paid": paid_v, "debt": debt})

    return ReportData(
        title="Qarzdorlik hisoboti",
        columns=[
            ReportColumn(key="client", header="Mijoz"),
            ReportColumn(key="invoiced", header="Hisoblangan"),
            ReportColumn(key="paid", header="Tolangan"),
            ReportColumn(key="debt", header="Qarz"),
        ],
        rows=rows,
    )


async def _clients(db: AsyncSession, f: ReportQuery) -> ReportData:
    from app.models.models import Contract, Region

    cases_count_subq = (
        select(Case.client_id.label("client_id"), func.count().label("cnt"))
        .group_by(Case.client_id)
        .subquery()
    )
    contracts_count_subq = (
        select(Contract.client_id.label("client_id"), func.count().label("cnt"))
        .group_by(Contract.client_id)
        .subquery()
    )
    paid_subq = (
        select(Payment.client_id.label("client_id"), func.sum(Payment.amount).label("paid"))
        .where(
            Payment.deleted_at.is_(None),
            Payment.direction == PaymentDirection.INCOME,
            Payment.status == PaymentStatus.PAID,
        )
        .group_by(Payment.client_id)
        .subquery()
    )

    stmt = (
        select(
            Client.full_name,
            Region.name,
            cases_count_subq.c.cnt,
            contracts_count_subq.c.cnt,
            paid_subq.c.paid,
        )
        .select_from(Client)
        .outerjoin(Region, Region.id == Client.region_id)
        .outerjoin(cases_count_subq, cases_count_subq.c.client_id == Client.id)
        .outerjoin(contracts_count_subq, contracts_count_subq.c.client_id == Client.id)
        .outerjoin(paid_subq, paid_subq.c.client_id == Client.id)
        .where(Client.deleted_at.is_(None))
        .limit(5000)
    )
    if f.region_id:
        stmt = stmt.where(Client.region_id == f.region_id)

    rows = []
    for full_name, region_name, cases_cnt, contracts_cnt, paid in (await db.execute(stmt)).all():
        rows.append(
            {
                "client": full_name,
                "region": region_name or "-",
                "cases": cases_cnt or 0,
                "contracts": contracts_cnt or 0,
                "paid": _n(paid),
            }
        )

    return ReportData(
        title="Mijozlar hisoboti",
        columns=[
            ReportColumn(key="client", header="Mijoz"),
            ReportColumn(key="region", header="Hudud"),
            ReportColumn(key="cases", header="Ishlar"),
            ReportColumn(key="contracts", header="Shartnomalar"),
            ReportColumn(key="paid", header="Tolangan"),
        ],
        rows=rows,
    )


async def _employees(db: AsyncSession, f: ReportQuery) -> ReportData:
    stmt = select(Employee).where(Employee.deleted_at.is_(None)).options(
        selectinload(Employee.user).selectinload(User.profile)
    )
    if f.region_id:
        stmt = stmt.join(User, Employee.user_id == User.id).where(User.region_id == f.region_id)
    employees = (await db.execute(stmt)).scalars().all()

    rows = []
    for e in employees:
        staff_condition = (
            Case.lawyer_id.in_(select(Lawyer.id).where(Lawyer.user_id == e.user_id))
            | Case.advocate_id.in_(select(Advocate.id).where(Advocate.user_id == e.user_id))
        )
        cases_count = (
            await db.execute(
                select(func.count()).select_from(Case).where(Case.deleted_at.is_(None), staff_condition)
            )
        ).scalar_one()
        revenue_sum = (
            await db.execute(
                select(func.sum(Payment.amount))
                .join(Case, Payment.case_id == Case.id)
                .where(
                    Payment.status == PaymentStatus.PAID,
                    Payment.direction == PaymentDirection.INCOME,
                    staff_condition,
                )
            )
        ).scalar()
        revenue = _n(revenue_sum)
        pct = float(e.commission_percent or 0)
        profile: UserProfile | None = e.user.profile if e.user else None
        employee_name = f"{profile.last_name} {profile.first_name}" if profile else e.user_id
        rows.append(
            {
                "employee": employee_name,
                "kind": e.kind,
                "cases": cases_count,
                "revenue": revenue,
                "commissionPercent": pct,
                "commission": round(revenue * pct / 100),
            }
        )

    return ReportData(
        title="Xodimlar hisoboti",
        columns=[
            ReportColumn(key="employee", header="Xodim"),
            ReportColumn(key="kind", header="Turi"),
            ReportColumn(key="cases", header="Ishlar"),
            ReportColumn(key="revenue", header="Daromad"),
            ReportColumn(key="commissionPercent", header="Foiz"),
            ReportColumn(key="commission", header="Komissiya"),
        ],
        rows=rows,
    )


async def _services(db: AsyncSession, f: ReportQuery) -> ReportData:
    grouped_stmt = select(
        CaseService.service_id,
        func.sum(CaseService.unit_price),
        func.count(),
    ).group_by(CaseService.service_id)
    grouped = (await db.execute(grouped_stmt)).all()

    services_stmt = select(Service.id, Service.name, Service.category)
    if f.service_id:
        services_stmt = services_stmt.where(Service.id == f.service_id)
    services = {row[0]: row for row in (await db.execute(services_stmt)).all()}

    rows = []
    for service_id, unit_price_sum, count in grouped:
        if f.service_id and service_id != f.service_id:
            continue
        svc = services.get(service_id)
        rows.append(
            {
                "service": svc[1] if svc else service_id,
                "category": svc[2] if svc else "-",
                "count": count,
                "revenue": _n(unit_price_sum),
            }
        )

    return ReportData(
        title="Xizmatlar hisoboti",
        columns=[
            ReportColumn(key="service", header="Xizmat"),
            ReportColumn(key="category", header="Kategoriya"),
            ReportColumn(key="count", header="Marta"),
            ReportColumn(key="revenue", header="Daromad"),
        ],
        rows=rows,
    )


async def _cases(db: AsyncSession, f: ReportQuery) -> ReportData:
    stmt = select(Case).options(selectinload(Case.client)).where(Case.deleted_at.is_(None))
    if f.client_id:
        stmt = stmt.where(Case.client_id == f.client_id)
    if f.employee_id:
        stmt = stmt.where(Case.responsible_employee_id == f.employee_id)
    stmt = stmt.order_by(Case.created_at.desc()).limit(5000)
    rows = (await db.execute(stmt)).scalars().all()

    return ReportData(
        title="Ishlar hisoboti",
        columns=[
            ReportColumn(key="number", header="Raqam"),
            ReportColumn(key="title", header="Nomi"),
            ReportColumn(key="client", header="Mijoz"),
            ReportColumn(key="status", header="Holat"),
            ReportColumn(key="priority", header="Ustuvorlik"),
        ],
        rows=[
            {
                "number": c.number,
                "title": c.title,
                "client": c.client.full_name if c.client else "-",
                "status": c.status,
                "priority": c.priority,
            }
            for c in rows
        ],
    )
