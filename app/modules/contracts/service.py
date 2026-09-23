from __future__ import annotations

import time
from datetime import date, datetime
from app.core.timeutils import utcnow
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import and_, func, inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import build_page, to_paginated
from app.core.security import AuthUser
from app.models.enums import RoleKey
from app.models.models import Case, Contract, Employee, User
from app.modules.contracts.schemas import ContractQuery, CreateContractRequest, UpdateContractRequest

_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


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
    return f"CNT-{year}-{_base36_upper(int(time.time() * 1000))}"


# ======================================================================
# OBJECT-LEVEL SCOPE (contracts.service.js#scope ekvivalenti — bu modulga xos)
# ======================================================================


def _is_privileged(user: AuthUser) -> bool:
    keys = {RoleKey.SUPER_ADMIN.value, RoleKey.ADMIN.value, RoleKey.MANAGER.value, RoleKey.ACCOUNTANT.value}
    return any(r in keys for r in user.roles)


def _is_client(user: AuthUser) -> bool:
    return RoleKey.CLIENT.value in user.roles


def _scope_condition(user: AuthUser):
    if _is_privileged(user):
        return None
    if _is_client(user):
        return Contract.client_id == (user.client_id or "__none__")
    return or_(
        Contract.responsible_employee_id.in_(select(Employee.id).where(Employee.user_id == user.id)),
        Contract.case_id.in_(select(Case.id).where(Case.office_id == (user.office_id or "__none__"))),
    )


def _columns_dict(obj) -> dict:
    """Python-tomon snake_case atribut nomlari bilan (DB ustun nomi bilan EMAS)."""
    return {attr.key: getattr(obj, attr.key) for attr in inspect(obj).mapper.column_attrs}


def _serialize_employee_profile(employee: Employee | None) -> dict | None:
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


async def list_contracts(db: AsyncSession, query: ContractQuery, user: AuthUser) -> dict:
    page_info = build_page(query, default_sort="created_at")
    conditions = [Contract.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)
    if query.status:
        conditions.append(Contract.status == query.status)
    if query.client_id:
        conditions.append(Contract.client_id == query.client_id)
    if query.search:
        conditions.append(Contract.number.ilike(f"%{query.search}%"))
    where_clause = and_(*conditions)

    stmt = select(Contract).options(selectinload(Contract.client)).where(where_clause)
    sort_col = getattr(Contract, page_info["sort"], Contract.created_at)
    stmt = stmt.order_by(sort_col.desc() if page_info["order"] == "desc" else sort_col.asc())
    stmt = stmt.offset(page_info["skip"]).limit(page_info["take"])

    total = (await db.execute(select(func.count()).select_from(Contract).where(where_clause))).scalar_one()
    rows = (await db.execute(stmt)).scalars().all()

    items = []
    for c in rows:
        data = _columns_dict(c)
        data["client"] = {"id": c.client.id, "full_name": c.client.full_name} if c.client else None
        items.append(data)
    return to_paginated(items, total, page_info["page"], page_info["limit"])


async def get_contract(db: AsyncSession, contract_id: str, user: AuthUser) -> dict:
    conditions = [Contract.id == contract_id, Contract.deleted_at.is_(None)]
    scope_cond = _scope_condition(user)
    if scope_cond is not None:
        conditions.append(scope_cond)

    contract = (
        await db.execute(
            select(Contract)
            .options(
                selectinload(Contract.client),
                selectinload(Contract.responsible_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(Contract.documents),
            )
            .where(and_(*conditions))
        )
    ).scalar_one_or_none()
    if contract is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shartnoma topilmadi")

    docs = [d for d in contract.documents if d.deleted_at is None]
    data = _columns_dict(contract)
    data["client"] = _columns_dict(contract.client) if contract.client else None
    data["responsible_employee"] = _serialize_employee_profile(contract.responsible_employee)
    data["documents"] = [_columns_dict(d) for d in docs]
    return data


async def create_contract(db: AsyncSession, dto: CreateContractRequest) -> dict:
    # MUHIM: asl contracts.controller.js#create hech qanday foydalanuvchi/scope
    # tekshiruvi qilmaydi (faqat contracts.create ruxsatiga tayanadi) — shu bilan
    # bir xil; fileStorageKey/fileName maydonlari asl kodda HECH QAYERDA
    # to'ldirilmagan (grep bilan tekshirildi) — shu sababli bu yerda ham
    # fayl yuklash oqimi yo'q, faqat model ustunlari sifatida mavjud.
    contract = Contract(
        number=_generate_number(),
        client_id=dto.client_id,
        case_id=dto.case_id,
        responsible_employee_id=dto.responsible_employee_id,
        amount=Decimal(str(dto.amount)) if dto.amount is not None else None,
        currency=dto.currency or "UZS",
        commission_percent=Decimal(str(dto.commission_percent)) if dto.commission_percent is not None else None,
        start_date=date.fromisoformat(dto.start_date) if dto.start_date else None,
        end_date=date.fromisoformat(dto.end_date) if dto.end_date else None,
    )
    db.add(contract)
    await db.commit()
    return _columns_dict(contract)


async def update_contract(db: AsyncSession, contract_id: str, dto: UpdateContractRequest, user: AuthUser) -> dict:
    await get_contract(db, contract_id, user)  # scope + mavjudlik tekshiruvi (asl kod: this.get(id, user))
    contract = (await db.execute(select(Contract).where(Contract.id == contract_id))).scalar_one()

    if dto.status is not None:
        contract.status = dto.status
    if dto.amount is not None:
        contract.amount = Decimal(str(dto.amount))
    if dto.currency is not None:
        contract.currency = dto.currency
    if dto.commission_percent is not None:
        contract.commission_percent = Decimal(str(dto.commission_percent))
    if dto.start_date is not None:
        contract.start_date = date.fromisoformat(dto.start_date)
    if dto.end_date is not None:
        contract.end_date = date.fromisoformat(dto.end_date)
    if dto.responsible_employee_id is not None:
        contract.responsible_employee_id = dto.responsible_employee_id

    await db.commit()
    return _columns_dict(contract)


async def remove_contract(db: AsyncSession, contract_id: str, user: AuthUser) -> dict:
    await get_contract(db, contract_id, user)
    contract = (await db.execute(select(Contract).where(Contract.id == contract_id))).scalar_one()
    contract.deleted_at = utcnow()
    await db.commit()
    return {"ok": True}
