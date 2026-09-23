from __future__ import annotations

import time
from datetime import datetime
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import AuthUser
from app.models.enums import ClientType, PaymentStatus, RoleKey, TimelineEventType
from app.models.models import (
    Case,
    Client,
    Contract,
    Document,
    Employee,
    Invoice,
    Payment,
    TimelineEvent,
    User,
    UserProfile,
)
from app.modules.clients.schemas import ClientQuery, CreateClientRequest, TimelineNoteRequest, UpdateClientRequest

_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _base36_upper(n: int) -> str:
    """Date.now().toString(36).toUpperCase() ekvivalenti."""
    if n == 0:
        return "0"
    out: list[str] = []
    while n:
        n, r = divmod(n, 36)
        out.append(_DIGITS[r])
    return "".join(reversed(out))


def _generate_code() -> str:
    return f"CL-{_base36_upper(int(time.time() * 1000))}"


# ======================================================================
# OBJECT-LEVEL SCOPE (clients.service.js#scope — bu modulga xos, umumiy
# object_access.scope_by_client'dan farqli: Client yozuvining o'zi
# client_id ustuniga ega emas, shuning uchun generic helper mos kelmaydi).
# ======================================================================


def _is_privileged(user: AuthUser) -> bool:
    keys = {RoleKey.SUPER_ADMIN.value, RoleKey.ADMIN.value, RoleKey.MANAGER.value}
    return any(r in keys for r in user.roles)


def _is_client(user: AuthUser) -> bool:
    return RoleKey.CLIENT.value in user.roles


def _scope_condition(user: AuthUser):
    """None -> cheklovsiz; aks holda WHERE ga qo'shiladigan shart."""
    if _is_privileged(user):
        return None
    if _is_client(user):
        return Client.id == (user.client_id or "__none__")
    conditions = []
    if user.region_id:
        conditions.append(Client.region_id == user.region_id)
    conditions.append(
        Client.responsible_employee_id.in_(select(Employee.id).where(Employee.user_id == user.id))
    )
    return or_(*conditions)


# ======================================================================
# TIMELINE (clients/timeline.service.js ekvivalenti)
# ======================================================================


async def record_timeline_event(
    db: AsyncSession,
    *,
    client_id: str,
    type: TimelineEventType,
    title: str,
    description: str | None = None,
    actor_id: str | None = None,
    meta: dict | None = None,
) -> TimelineEvent:
    event = TimelineEvent(
        client_id=client_id,
        type=type,
        title=title,
        description=description,
        actor_id=actor_id,
        meta=meta,
    )
    db.add(event)
    await db.flush()
    return event


async def list_timeline(db: AsyncSession, client_id: str, take: int = 50) -> list[TimelineEvent]:
    rows = (
        await db.execute(
            select(TimelineEvent)
            .where(TimelineEvent.client_id == client_id)
            .order_by(TimelineEvent.occurred_at.desc())
            .limit(take)
        )
    ).scalars().all()
    return list(rows)


def _serialize_timeline(event: TimelineEvent) -> dict:
    return {
        "id": event.id,
        "client_id": event.client_id,
        "type": event.type,
        "title": event.title,
        "description": event.description,
        "actor_id": event.actor_id,
        "meta": event.meta,
        "occurred_at": event.occurred_at,
    }


# ======================================================================
# SERIALIZATION
# ======================================================================


def _serialize_region(region) -> dict | None:
    if region is None:
        return None
    return {"id": region.id, "name": region.name}


def _serialize_responsible_employee(employee: Employee | None) -> dict | None:
    if employee is None:
        return None
    profile = employee.user.profile if employee.user and employee.user.profile else None
    return {
        "id": employee.id,
        "user": {
            "profile": (
                {"first_name": profile.first_name, "last_name": profile.last_name} if profile else None
            )
        },
    }


def _serialize_basic(client: Client) -> dict:
    return {
        "id": client.id,
        "code": client.code,
        "full_name": client.full_name,
        "client_type": client.client_type,
        "phone": client.phone,
        "email": client.email,
        "address": client.address,
        "tax_id": client.tax_id,
        "region_id": client.region_id,
        "responsible_employee_id": client.responsible_employee_id,
        "first_contact_at": client.first_contact_at,
        "created_at": client.created_at,
        "updated_at": client.updated_at,
    }


def _serialize_list_item(client: Client, case_count: int, contract_count: int) -> dict:
    data = _serialize_basic(client)
    data["region"] = _serialize_region(client.region)
    data["responsible_employee"] = _serialize_responsible_employee(client.responsible_employee)
    data["count"] = {"cases": case_count, "contracts": contract_count}
    return data


# ======================================================================
# CRUD
# ======================================================================


async def list_clients(db: AsyncSession, query: ClientQuery, user: AuthUser) -> dict:
    from app.core.pagination import build_page, to_paginated

    page_info = build_page(query, default_sort="created_at")
    conditions = [Client.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)
    if query.region_id:
        conditions.append(Client.region_id == query.region_id)
    if query.responsible_employee_id:
        conditions.append(Client.responsible_employee_id == query.responsible_employee_id)
    if query.search:
        like = f"%{query.search}%"
        conditions.append(
            or_(
                Client.full_name.ilike(like),
                Client.phone.ilike(like),
                Client.email.ilike(like),
                Client.code.ilike(like),
            )
        )
    where_clause = and_(*conditions)

    stmt = (
        select(Client)
        .options(
            selectinload(Client.region),
            selectinload(Client.responsible_employee).selectinload(Employee.user).selectinload(User.profile),
        )
        .where(where_clause)
    )
    sort_col = getattr(Client, page_info["sort"], Client.created_at)
    stmt = stmt.order_by(sort_col.desc() if page_info["order"] == "desc" else sort_col.asc())
    stmt = stmt.offset(page_info["skip"]).limit(page_info["take"])

    count_stmt = select(func.count()).select_from(Client).where(where_clause)
    total = (await db.execute(count_stmt)).scalar_one()
    rows = (await db.execute(stmt)).scalars().all()

    ids = [c.id for c in rows]
    case_counts: dict[str, int] = {}
    contract_counts: dict[str, int] = {}
    if ids:
        case_rows = (
            await db.execute(
                select(Case.client_id, func.count())
                .where(Case.client_id.in_(ids), Case.deleted_at.is_(None))
                .group_by(Case.client_id)
            )
        ).all()
        case_counts = dict(case_rows)
        contract_rows = (
            await db.execute(
                select(Contract.client_id, func.count())
                .where(Contract.client_id.in_(ids), Contract.deleted_at.is_(None))
                .group_by(Contract.client_id)
            )
        ).all()
        contract_counts = dict(contract_rows)

    items = [_serialize_list_item(c, case_counts.get(c.id, 0), contract_counts.get(c.id, 0)) for c in rows]
    return to_paginated(items, total, page_info["page"], page_info["limit"])


async def get_client(db: AsyncSession, client_id: str, user: AuthUser) -> dict:
    conditions = [Client.id == client_id, Client.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)

    client = (
        await db.execute(
            select(Client)
            .options(
                selectinload(Client.region),
                selectinload(Client.responsible_employee).selectinload(Employee.user).selectinload(User.profile),
            )
            .where(and_(*conditions))
        )
    ).scalar_one_or_none()
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mijoz topilmadi")

    async def _count(model, extra=()) -> int:
        stmt = select(func.count()).select_from(model).where(model.client_id == client_id, model.deleted_at.is_(None), *extra)
        return (await db.execute(stmt)).scalar_one()

    cases_count = await _count(Case)
    contracts_count = await _count(Contract)
    invoices_count = await _count(Invoice)
    documents_count = await _count(Document)
    payments_count = await _count(Payment)

    paid_sum = (
        await db.execute(
            select(func.sum(Payment.amount)).where(Payment.client_id == client_id, Payment.status == PaymentStatus.PAID)
        )
    ).scalar_one_or_none()

    timeline = await list_timeline(db, client_id)

    data = _serialize_basic(client)
    data["region"] = _serialize_region(client.region)
    data["responsible_employee"] = _serialize_responsible_employee(client.responsible_employee)
    data["stats"] = {
        "cases": cases_count,
        "contracts": contracts_count,
        "invoices": invoices_count,
        "documents": documents_count,
        "payments": payments_count,
        "total_paid": paid_sum or 0,
    }
    data["timeline"] = [_serialize_timeline(ev) for ev in timeline]
    return data


async def create_client(db: AsyncSession, dto: CreateClientRequest, user: AuthUser) -> dict:
    client = Client(
        code=_generate_code(),
        full_name=dto.full_name,
        client_type=dto.client_type or ClientType.INDIVIDUAL,
        phone=dto.phone,
        email=dto.email,
        address=dto.address,
        tax_id=dto.tax_id,
        region_id=dto.region_id,
        responsible_employee_id=dto.responsible_employee_id,
        first_contact_at=utcnow(),
    )
    db.add(client)
    await db.flush()

    await record_timeline_event(
        db,
        client_id=client.id,
        type=TimelineEventType.CREATED,
        title="Mijoz yaratildi",
        actor_id=user.id,
    )
    await db.commit()
    return _serialize_basic(client)


async def _find_scoped(db: AsyncSession, client_id: str, user: AuthUser) -> Client:
    conditions = [Client.id == client_id, Client.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)
    client = (await db.execute(select(Client).where(and_(*conditions)))).scalar_one_or_none()
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mijoz topilmadi")
    return client


async def update_client(db: AsyncSession, client_id: str, dto: UpdateClientRequest, user: AuthUser) -> dict:
    existing = await _find_scoped(db, client_id, user)
    previous_responsible_employee_id = existing.responsible_employee_id

    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)

    if dto.responsible_employee_id and dto.responsible_employee_id != previous_responsible_employee_id:
        await record_timeline_event(
            db,
            client_id=client_id,
            type=TimelineEventType.STATUS_CHANGED,
            title="Mas'ul xodim o'zgartirildi",
            actor_id=user.id,
        )

    await db.commit()
    return _serialize_basic(existing)


async def remove_client(db: AsyncSession, client_id: str, user: AuthUser) -> dict:
    existing = await _find_scoped(db, client_id, user)
    existing.deleted_at = utcnow()
    await db.commit()
    return {"ok": True}


async def add_note(db: AsyncSession, client_id: str, dto: TimelineNoteRequest, user: AuthUser) -> dict:
    await get_client(db, client_id, user)  # scope tekshiruvi (asl kod bilan bir xil)
    event = await record_timeline_event(
        db,
        client_id=client_id,
        type=TimelineEventType.NOTE,
        title=dto.title,
        description=dto.description,
        actor_id=user.id,
    )
    await db.commit()
    return _serialize_timeline(event)
