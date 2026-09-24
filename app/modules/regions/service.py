"""regions.controller.js ekvivalenti — Prisma xizmat qatlamini oʻz ichiga olmagan,
mantiq toʻgʻridan-toʻgʻri controllerda edi, shu sababli shu yerda ham toʻgʻridan-toʻgʻri
DB amallari sifatida saqlandi."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import District, Region
from app.modules.regions.schemas import DistrictCreateRequest, RegionCreateRequest, RegionUpdateRequest

_LOAD = (selectinload(Region.offices), selectinload(Region.clients), selectinload(Region.districts))


def _serialize(region: Region) -> dict:
    return {
        "id": region.id,
        "code": region.code,
        "name": region.name,
        "created_at": region.created_at,
        "updated_at": region.updated_at,
        "count": {
            "offices": len(region.offices),
            "clients": len(region.clients),
            "districts": len(region.districts),
        },
        "districts": [{"id": d.id, "name": d.name} for d in region.districts],
    }


async def list_regions(db: AsyncSession) -> list[dict]:
    rows = (await db.execute(select(Region).options(*_LOAD).order_by(Region.name.asc()))).scalars().all()
    return [_serialize(r) for r in rows]


async def create_region(db: AsyncSession, dto: RegionCreateRequest) -> dict:
    region = Region(name=dto.name, code=dto.code)
    db.add(region)
    await db.commit()
    return _serialize(await _get_raw(db, region.id))


async def _get_raw(db: AsyncSession, region_id: str) -> Region:
    region = (
        await db.execute(select(Region).options(*_LOAD).where(Region.id == region_id).execution_options(populate_existing=True))
    ).scalar_one_or_none()
    if region is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
    return region


async def update_region(db: AsyncSession, region_id: str, dto: RegionUpdateRequest) -> dict:
    region = await _get_raw(db, region_id)
    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(region, field, value)
    await db.commit()
    return _serialize(await _get_raw(db, region_id))


async def add_district(db: AsyncSession, region_id: str, dto: DistrictCreateRequest) -> dict:
    region = await _get_raw(db, region_id)
    name = dto.name.strip()
    if any(d.name.lower() == name.lower() for d in region.districts):
        raise HTTPException(status.HTTP_409_CONFLICT, "Bu viloyatda shunday tuman allaqachon bor")
    db.add(District(region_id=region.id, name=name))
    await db.commit()
    return _serialize(await _get_raw(db, region_id))


async def remove_district(db: AsyncSession, region_id: str, district_id: str) -> dict:
    district = (
        await db.execute(select(District).where(District.id == district_id, District.region_id == region_id))
    ).scalar_one_or_none()
    if district is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topilmadi")
    await db.delete(district)
    await db.commit()
    return _serialize(await _get_raw(db, region_id))


async def remove_region(db: AsyncSession, region_id: str) -> dict:
    region = await _get_raw(db, region_id)
    result = _serialize(region)
    await db.delete(region)
    await db.commit()
    return result
