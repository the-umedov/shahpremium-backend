from __future__ import annotations

import time
from datetime import datetime
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import and_, func, inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import build_page, to_paginated
from app.core.security import AuthUser
from app.models.enums import CasePriority, CaseStatus, RoleKey
from app.models.models import (
    Advocate,
    Appointment,
    Case,
    CaseNote,
    Client,
    Contract,
    Document,
    Employee,
    Lawyer,
    Payment,
    Task,
    User,
)
from app.modules.cases.schemas import CaseNoteRequest, CaseQuery, CreateCaseRequest, UpdateCaseRequest

_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_CLOSED_STATUSES = {CaseStatus.CLOSED, CaseStatus.COMPLETED, CaseStatus.CANCELLED, CaseStatus.ARCHIVED}


def _base36_upper(n: int) -> str:
    if n == 0:
        return "0"
    out: list[str] = []
    while n:
        n, r = divmod(n, 36)
        out.append(_DIGITS[r])
    return "".join(reversed(out))


def _generate_number() -> str:
    year = utcnow().year
    return f"CASE-{year}-{_base36_upper(int(time.time() * 1000))}"


# ======================================================================
# OBJECT-LEVEL SCOPE (cases.service.js#scope ekvivalenti — bu modulga xos)
# ======================================================================


def _is_privileged(user: AuthUser) -> bool:
    keys = {RoleKey.SUPER_ADMIN.value, RoleKey.ADMIN.value, RoleKey.MANAGER.value}
    return any(r in keys for r in user.roles)


def _is_client(user: AuthUser) -> bool:
    return RoleKey.CLIENT.value in user.roles


def _scope_condition(user: AuthUser):
    if _is_privileged(user):
        return None
    if _is_client(user):
        return Case.client_id == (user.client_id or "__none__")
    conditions = []
    if user.office_id:
        conditions.append(Case.office_id == user.office_id)
    conditions.append(Case.responsible_employee_id.in_(select(Employee.id).where(Employee.user_id == user.id)))
    conditions.append(Case.lawyer_id.in_(select(Lawyer.id).where(Lawyer.user_id == user.id)))
    conditions.append(Case.advocate_id.in_(select(Advocate.id).where(Advocate.user_id == user.id)))
    return or_(*conditions)


def _columns_dict(obj) -> dict:
    """Python-tomon snake_case atribut nomlari bilan (DB ustun nomi bilan EMAS —
    ular endi haqiqiy Prisma camelCase nomlariga mos, masalan "caseType")."""
    return {attr.key: getattr(obj, attr.key) for attr in inspect(obj).mapper.column_attrs}


def _serialize_profile_holder(entity) -> dict | None:
    if entity is None:
        return None
    profile = entity.user.profile if entity.user and entity.user.profile else None
    return {
        "id": entity.id,
        "user": {
            "profile": (
                {"first_name": profile.first_name, "last_name": profile.last_name} if profile else None
            )
        },
    }


async def list_cases(db: AsyncSession, query: CaseQuery, user: AuthUser) -> dict:
    page_info = build_page(query, default_sort="created_at")
    conditions = [Case.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)
    if query.status:
        conditions.append(Case.status == query.status)
    if query.priority:
        conditions.append(Case.priority == query.priority)
    if query.client_id:
        conditions.append(Case.client_id == query.client_id)
    if query.responsible_employee_id:
        conditions.append(Case.responsible_employee_id == query.responsible_employee_id)
    if query.search:
        like = f"%{query.search}%"
        conditions.append(or_(Case.number.ilike(like), Case.title.ilike(like)))
    where_clause = and_(*conditions)

    stmt = (
        select(Case)
        .options(
            selectinload(Case.client),
            selectinload(Case.responsible_employee).selectinload(Employee.user).selectinload(User.profile),
        )
        .where(where_clause)
    )
    sort_col = getattr(Case, page_info["sort"], Case.created_at)
    stmt = stmt.order_by(sort_col.desc() if page_info["order"] == "desc" else sort_col.asc())
    stmt = stmt.offset(page_info["skip"]).limit(page_info["take"])

    total = (await db.execute(select(func.count()).select_from(Case).where(where_clause))).scalar_one()
    rows = (await db.execute(stmt)).scalars().all()

    ids = [c.id for c in rows]
    doc_counts: dict[str, int] = {}
    task_counts: dict[str, int] = {}
    contract_counts: dict[str, int] = {}
    if ids:
        doc_counts = dict(
            (await db.execute(select(Document.case_id, func.count()).where(Document.case_id.in_(ids)).group_by(Document.case_id))).all()
        )
        task_counts = dict(
            (await db.execute(select(Task.case_id, func.count()).where(Task.case_id.in_(ids)).group_by(Task.case_id))).all()
        )
        contract_counts = dict(
            (await db.execute(select(Contract.case_id, func.count()).where(Contract.case_id.in_(ids)).group_by(Contract.case_id))).all()
        )

    items = []
    for c in rows:
        data = _columns_dict(c)
        data["client"] = {"id": c.client.id, "full_name": c.client.full_name} if c.client else None
        data["responsible_employee"] = _serialize_profile_holder(c.responsible_employee)
        data["count"] = {
            "documents": doc_counts.get(c.id, 0),
            "tasks": task_counts.get(c.id, 0),
            "contracts": contract_counts.get(c.id, 0),
        }
        items.append(data)
    return to_paginated(items, total, page_info["page"], page_info["limit"])


async def get_case(db: AsyncSession, case_id: str, user: AuthUser) -> dict:
    conditions = [Case.id == case_id, Case.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)

    legal_case = (
        await db.execute(
            select(Case)
            .options(
                selectinload(Case.client),
                selectinload(Case.responsible_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(Case.lawyer).selectinload(Lawyer.user).selectinload(User.profile),
                selectinload(Case.documents),
                selectinload(Case.contracts),
                selectinload(Case.tasks),
                selectinload(Case.appointments),
                selectinload(Case.payments),
                selectinload(Case.notes),
            )
            .where(and_(*conditions))
        )
    ).unique().scalar_one_or_none()
    if legal_case is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ish topilmadi")

    docs = sorted((d for d in legal_case.documents if d.deleted_at is None), key=lambda d: d.created_at, reverse=True)
    contracts = [c for c in legal_case.contracts if c.deleted_at is None]
    tasks = sorted((t for t in legal_case.tasks if t.deleted_at is None), key=lambda t: t.created_at, reverse=True)
    appointments = sorted(legal_case.appointments, key=lambda a: a.start_at, reverse=True)
    notes = sorted(legal_case.notes, key=lambda n: n.created_at, reverse=True)

    data = _columns_dict(legal_case)
    data["client"] = (
        {"id": legal_case.client.id, "full_name": legal_case.client.full_name, "phone": legal_case.client.phone}
        if legal_case.client
        else None
    )
    data["responsible_employee"] = _serialize_profile_holder(legal_case.responsible_employee)
    data["lawyer"] = _serialize_profile_holder(legal_case.lawyer)
    data["documents"] = [_columns_dict(d) for d in docs]
    data["contracts"] = [_columns_dict(c) for c in contracts]
    data["tasks"] = [_columns_dict(t) for t in tasks]
    data["appointments"] = [_columns_dict(a) for a in appointments]
    data["payments"] = [_columns_dict(p) for p in legal_case.payments]
    data["notes"] = [_columns_dict(n) for n in notes]
    return data


async def create_case(db: AsyncSession, dto: CreateCaseRequest, user: AuthUser) -> dict:
    case = Case(
        number=_generate_number(),
        title=dto.title,
        description=dto.description,
        case_type=dto.case_type,
        category=dto.category,
        priority=dto.priority or CasePriority.NORMAL,
        status=CaseStatus.NEW,
        opened_at=utcnow(),
        client_id=dto.client_id,
        responsible_employee_id=dto.responsible_employee_id,
        lawyer_id=dto.lawyer_id,
        office_id=dto.office_id or user.office_id,
    )
    db.add(case)
    await db.commit()
    return _columns_dict(case)


async def _find_scoped(db: AsyncSession, case_id: str, user: AuthUser) -> Case:
    conditions = [Case.id == case_id, Case.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)
    case = (await db.execute(select(Case).where(and_(*conditions)))).scalar_one_or_none()
    if case is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ish topilmadi")
    return case


async def update_case(db: AsyncSession, case_id: str, dto: UpdateCaseRequest, user: AuthUser) -> dict:
    case = await _find_scoped(db, case_id, user)
    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    # Asl kodda (cases.service.js#update) status o'zgarishi TimelineEvent yozmaydi —
    # timeline faqat clients moduli orqali yuritiladi; shu bilan faqat closedAt yangilanadi.
    if dto.status and dto.status in _CLOSED_STATUSES:
        case.closed_at = utcnow()
    await db.commit()
    return _columns_dict(case)


async def remove_case(db: AsyncSession, case_id: str, user: AuthUser) -> dict:
    case = await _find_scoped(db, case_id, user)
    case.deleted_at = utcnow()
    await db.commit()
    return {"ok": True}


async def add_note(db: AsyncSession, case_id: str, dto: CaseNoteRequest, user: AuthUser) -> dict:
    await _find_scoped(db, case_id, user)
    note = CaseNote(case_id=case_id, body=dto.body, author_id=user.id)
    db.add(note)
    await db.commit()
    return _columns_dict(note)
