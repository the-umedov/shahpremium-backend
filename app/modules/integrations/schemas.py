from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.models.enums import IntegrationType, PartnerStatus


class IntegrationUpsertRequest(BaseModel):
    key: str
    name: str
    type: IntegrationType | None = None
    is_enabled: bool | None = None
    config: dict[str, Any] | None = None


class PartnerCreateRequest(BaseModel):
    name: str
    description: str | None = None
    contacts: dict[str, Any] | None = None
    contract_number: str | None = None
    contract_ends_at: str | None = None
    services: list[str] | None = None
    status: PartnerStatus | None = None


class PartnerUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    contacts: dict[str, Any] | None = None
    contract_number: str | None = None
    contract_ends_at: str | None = None
    services: list[str] | None = None
    status: PartnerStatus | None = None
