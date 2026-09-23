from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Integration, PartnerOrganization
from app.modules.integrations.schemas import (
    IntegrationUpsertRequest,
    PartnerCreateRequest,
    PartnerUpdateRequest,
)

# integrations/abstraction.js#INTEGRATION_CATALOG — aynan asl qiymatlar bilan.
INTEGRATION_CATALOG: list[dict[str, str]] = [
    {"type": "PAYMENT", "label": "To'lov shluzlari (Payme, Click)"},
    {"type": "EMAIL", "label": "Email yuborish"},
    {"type": "SMS", "label": "SMS yuborish"},
    {"type": "MAPS", "label": "Xaritalar"},
    {"type": "CALENDAR", "label": "Tashqi taqvimlar (Google/Outlook)"},
    {"type": "EXTERNAL_ORG", "label": "Tashqi tashkilotlar / reyestrlar"},
    {"type": "ACCOUNTING", "label": "Buxgalteriya tizimlari"},
    {"type": "EDMS", "label": "Elektron hujjat aylanishi"},
]


def catalog() -> list[dict[str, str]]:
    return INTEGRATION_CATALOG


async def list_integrations(db: AsyncSession) -> list[Integration]:
    rows = (await db.execute(select(Integration).order_by(Integration.name.asc()))).scalars().all()
    return list(rows)


async def upsert_integration(db: AsyncSession, dto: IntegrationUpsertRequest) -> Integration:
    existing = (await db.execute(select(Integration).where(Integration.key == dto.key))).scalar_one_or_none()
    if existing:
        existing.name = dto.name
        existing.type = dto.type
        existing.is_enabled = dto.is_enabled if dto.is_enabled is not None else existing.is_enabled
        existing.config = dto.config
        integration = existing
    else:
        integration = Integration(
            key=dto.key,
            name=dto.name,
            type=dto.type,
            is_enabled=dto.is_enabled or False,
            config=dto.config,
        )
        db.add(integration)
    await db.commit()
    return integration


async def list_partners(db: AsyncSession) -> list[PartnerOrganization]:
    rows = (
        await db.execute(select(PartnerOrganization).order_by(PartnerOrganization.name.asc()))
    ).scalars().all()
    return list(rows)


async def create_partner(db: AsyncSession, dto: PartnerCreateRequest) -> PartnerOrganization:
    partner = PartnerOrganization(
        name=dto.name,
        description=dto.description,
        contacts=dto.contacts,
        contract_number=dto.contract_number,
        contract_ends_at=datetime.fromisoformat(dto.contract_ends_at) if dto.contract_ends_at else None,
        services=dto.services or [],
        status=dto.status or "ACTIVE",
    )
    db.add(partner)
    await db.commit()
    return partner


async def update_partner(db: AsyncSession, partner_id: str, dto: PartnerUpdateRequest) -> PartnerOrganization:
    partner = (
        await db.execute(select(PartnerOrganization).where(PartnerOrganization.id == partner_id))
    ).scalar_one_or_none()
    if partner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hamkor tashkilot topilmadi")
    data = dto.model_dump(exclude_unset=True)
    if data.get("contract_ends_at"):
        data["contract_ends_at"] = datetime.fromisoformat(data["contract_ends_at"])
    for field, value in data.items():
        setattr(partner, field, value)
    await db.commit()
    return partner


async def remove_partner(db: AsyncSession, partner_id: str) -> dict:
    partner = (
        await db.execute(select(PartnerOrganization).where(PartnerOrganization.id == partner_id))
    ).scalar_one_or_none()
    if partner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Hamkor tashkilot topilmadi")
    await db.delete(partner)
    await db.commit()
    return {"ok": True}
