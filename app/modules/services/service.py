"""services.service.js ekvivalenti — yuridik xizmatlar katalogi (soft-delete yoʻq,
`Service` modelida `deleted_at` ustuni ham yoʻq — asl kodda ham topilmagan)."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginationQuery, to_paginated
from app.models.enums import ServiceCategory
from app.models.models import Service
from app.modules.services.schemas import (
    ReorderItem,
    ServiceCreateRequest,
    ServiceUpdateRequest,
)


def _serialize(service: Service) -> dict:
    return {
        "id": service.id,
        "code": service.code,
        "name": service.name,
        "description": service.description,
        "category": service.category,
        "base_price": service.base_price,
        "sort_order": service.sort_order,
        "is_active": service.is_active,
        "created_at": service.created_at,
        "updated_at": service.updated_at,
    }


async def list_services(
    db: AsyncSession,
    query: PaginationQuery,
    category: ServiceCategory | None,
    active: str | None,
) -> dict:
    page = max(1, query.page or 1)
    limit = min(100, max(1, query.limit or 20))
    skip = (page - 1) * limit
    # Asl kodda order ni bermasa "asc" default qilinadi; umumiy PaginationQuery
    # modelida esa "desc" default — bu yerda ushbu farqni ataylab saqlab qoldik
    # (umumiy infra ustunligi), faqat shu qatorga izoh sifatida qayd etildi.
    order_desc = query.order == "desc"

    stmt = select(Service)
    count_stmt = select(func.count()).select_from(Service)
    if category:
        stmt = stmt.where(Service.category == category)
        count_stmt = count_stmt.where(Service.category == category)
    if active == "true":
        stmt = stmt.where(Service.is_active.is_(True))
        count_stmt = count_stmt.where(Service.is_active.is_(True))
    elif active == "false":
        stmt = stmt.where(Service.is_active.is_(False))
        count_stmt = count_stmt.where(Service.is_active.is_(False))
    if query.search:
        clause = or_(Service.name.ilike(f"%{query.search}%"), Service.code.ilike(f"%{query.search}%"))
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)

    total = (await db.execute(count_stmt)).scalar_one()
    order_col = Service.sort_order.desc() if order_desc else Service.sort_order.asc()
    rows = (
        await db.execute(stmt.order_by(order_col).offset(skip).limit(limit))
    ).scalars().all()

    return to_paginated([_serialize(s) for s in rows], total, page, limit)


async def get_service(db: AsyncSession, service_id: str) -> Service:
    service = (
        await db.execute(select(Service).where(Service.id == service_id))
    ).scalar_one_or_none()
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Xizmat topilmadi")
    return service


async def get_service_dict(db: AsyncSession, service_id: str) -> dict:
    return _serialize(await get_service(db, service_id))


async def create_service(db: AsyncSession, dto: ServiceCreateRequest) -> dict:
    service = Service(
        code=dto.code,
        name=dto.name,
        description=dto.description,
        category=dto.category,
        base_price=Decimal(str(dto.base_price)) if dto.base_price is not None else None,
        sort_order=dto.sort_order if dto.sort_order is not None else 0,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return _serialize(service)


async def update_service(db: AsyncSession, service_id: str, dto: ServiceUpdateRequest) -> dict:
    service = await get_service(db, service_id)
    data = dto.model_dump(exclude_unset=True)
    if "base_price" in data:
        if data["base_price"] is None:
            # Asl kodda `basePrice != null ? Decimal(...) : undefined` — null bo'lsa
            # ham maydon o'zgarmaydi (undefined bilan bir xil ishlangan).
            data.pop("base_price")
        else:
            data["base_price"] = Decimal(str(data["base_price"]))
    for field, value in data.items():
        setattr(service, field, value)
    await db.commit()
    await db.refresh(service)
    return _serialize(service)


async def set_active(db: AsyncSession, service_id: str, is_active: bool) -> dict:
    service = await get_service(db, service_id)
    service.is_active = is_active
    await db.commit()
    await db.refresh(service)
    return _serialize(service)


async def reorder_services(db: AsyncSession, items: list[ReorderItem]) -> dict:
    for item in items:
        service = await get_service(db, item.id)
        service.sort_order = item.sort_order
    await db.commit()
    return {"updated": len(items)}
