from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.modules.regions.schemas import DistrictCreateRequest, RegionCreateRequest, RegionUpdateRequest
from app.modules.regions.service import (
    add_district,
    create_region,
    list_regions,
    remove_district,
    remove_region,
    update_region,
)

router = APIRouter(tags=["regions"])

_manage = Depends(require_permissions("regions.manage"))


@router.get("")
async def list_regions_route(db: DbSession) -> list[dict]:
    return await list_regions(db)


@router.post("", status_code=201, dependencies=[_manage])
async def create_region_route(dto: RegionCreateRequest, db: DbSession) -> dict:
    return await create_region(db, dto)


@router.put("/{region_id}", dependencies=[_manage])
async def update_region_route(region_id: str, dto: RegionUpdateRequest, db: DbSession) -> dict:
    return await update_region(db, region_id, dto)


@router.delete("/{region_id}", dependencies=[_manage])
async def remove_region_route(region_id: str, db: DbSession) -> dict:
    return await remove_region(db, region_id)


@router.post("/{region_id}/districts", status_code=201, dependencies=[_manage])
async def add_district_route(region_id: str, dto: DistrictCreateRequest, db: DbSession) -> dict:
    return await add_district(db, region_id, dto)


@router.delete("/{region_id}/districts/{district_id}", dependencies=[_manage])
async def remove_district_route(region_id: str, district_id: str, db: DbSession) -> dict:
    return await remove_district(db, region_id, district_id)
