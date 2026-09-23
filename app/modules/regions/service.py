"""regions.controller.js ekvivalenti — Prisma xizmat qatlamini oʻz ichiga olmagan,
mantiq toʻgʻridan-toʻgʻri controllerda edi, shu sababli shu yerda ham toʻgʻridan-toʻgʻri
DB amallari sifatida saqlandi."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Region
from app.modules.regions.schemas import RegionCreateRequest, RegionUpdateRequest


def _serialize(region: Region) -> dict:
    return {
        "id": region.id,
        "code": region.code,
        "name": region.name,
        "created_at": region.created_at,
        "updated_at": region.updated_at,
        "count": {"offices": len(region.offices), "clients": len(region.clients)},
    }


async def list_regions(db: AsyncSession) -> list[dict]:
    rows = (
        await db.execute(
            select(Region)
            .options(selectinload(Region.offices), selectinload(Region.clients))
            .order_by(Region.name.asc())
        )
    ).scalars().all()
    return [_serialize(r) for r in rows]


async def create_region(db: AsyncSession, dto: RegionCreateRequest) -> dict:
    region = Region(name=dto.name, code=dto.code)
    db.add(region)
    await db.commit()
    await db.refresh(region, attribute_names=["offices", "clients"])
    return _serialize(region)


async def _get_raw(db: AsyncSession, region_id: str) -> Region:
    region = (
        await db.execute(
            select(Region)
            .options(selectinload(Region.offices), selectinload(Region.clients))
            .where(Region.id == region_id)
        )
    ).scalar_one_or_none()
    if region is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
    return region


async def update_region(db: AsyncSession, region_id: str, dto: RegionUpdateRequest) -> dict:
    region = await _get_raw(db, region_id)
    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(region, field, value)
    await db.commit()
    await db.refresh(region, attribute_names=["offices", "clients"])
    return _serialize(region)


async def remove_region(db: AsyncSession, region_id: str) -> dict:
    region = await _get_raw(db, region_id)
    result = _serialize(region)
    await db.delete(region)
    await db.commit()
    return result
