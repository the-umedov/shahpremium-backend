from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.modules.integrations import service
from app.modules.integrations.schemas import (
    IntegrationUpsertRequest,
    PartnerCreateRequest,
    PartnerUpdateRequest,
)

router = APIRouter(tags=["integrations"], dependencies=[Depends(require_permissions("integrations.manage"))])


# Abstraksiya katalogi (qo'llab-quvvatlanadigan turlar)
@router.get("/catalog")
async def get_catalog() -> list[dict[str, str]]:
    return service.catalog()


@router.get("")
async def list_integrations(db: DbSession) -> list:
    return await service.list_integrations(db)


@router.put("")
async def upsert_integration(dto: IntegrationUpsertRequest, db: DbSession):
    return await service.upsert_integration(db, dto)


# ---- Hamkor tashkilotlar ----
@router.get("/partners")
async def list_partners(db: DbSession) -> list:
    return await service.list_partners(db)


@router.post("/partners")
async def create_partner(dto: PartnerCreateRequest, db: DbSession):
    return await service.create_partner(db, dto)


@router.put("/partners/{partner_id}")
async def update_partner(partner_id: str, dto: PartnerUpdateRequest, db: DbSession):
    return await service.update_partner(db, partner_id, dto)


@router.delete("/partners/{partner_id}")
async def remove_partner(partner_id: str, db: DbSession) -> dict:
    return await service.remove_partner(db, partner_id)
