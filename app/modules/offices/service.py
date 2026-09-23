"""offices.controller.js ekvivalenti — asl kodda mantiq toʻgʻridan-toʻgʻri
controllerda edi (alohida service qatlami yoʻq)."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Office
from app.modules.offices.schemas import OfficeCreateRequest, OfficeUpdateRequest


def _serialize(office: Office) -> dict:
    return {
        "id": office.id,
        "name": office.name,
        "address": office.address,
        "region_id": office.region_id,
        "created_at": office.created_at,
        "updated_at": office.updated_at,
        "region": {"id": office.region.id, "name": office.region.name} if office.region else None,
    }


async def list_offices(db: AsyncSession) -> list[dict]:
    rows = (
        await db.execute(
            select(Office).options(selectinload(Office.region)).order_by(Office.name.asc())
        )
    ).scalars().all()
    return [_serialize(o) for o in rows]


async def create_office(db: AsyncSession, dto: OfficeCreateRequest) -> dict:
    office = Office(name=dto.name, address=dto.address, region_id=dto.region_id)
    db.add(office)
    await db.commit()
    await db.refresh(office, attribute_names=["region"])
    return _serialize(office)


async def _get_raw(db: AsyncSession, office_id: str) -> Office:
    office = (
        await db.execute(
            select(Office).options(selectinload(Office.region)).where(Office.id == office_id)
        )
    ).scalar_one_or_none()
    if office is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
    return office


async def update_office(db: AsyncSession, office_id: str, dto: OfficeUpdateRequest) -> dict:
    office = await _get_raw(db, office_id)
    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(office, field, value)
    await db.commit()
    await db.refresh(office, attribute_names=["region"])
    return _serialize(office)


async def remove_office(db: AsyncSession, office_id: str) -> dict:
    office = await _get_raw(db, office_id)
    result = _serialize(office)
    await db.delete(office)
    await db.commit()
    return result
