from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.contracts import service
from app.modules.contracts.schemas import ContractQuery, CreateContractRequest, UpdateContractRequest

router = APIRouter(tags=["contracts"])


@router.get("", dependencies=[Depends(require_permissions("contracts.read"))])
async def list_contracts(db: DbSession, user: CurrentUser, query: ContractQuery = Depends()) -> dict:
    return await service.list_contracts(db, query, user)


@router.get("/{contract_id}", dependencies=[Depends(require_permissions("contracts.read"))])
async def get_contract(contract_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.get_contract(db, contract_id, user)


@router.post("", status_code=201, dependencies=[Depends(require_permissions("contracts.create"))])
async def create_contract(dto: CreateContractRequest, db: DbSession) -> dict:
    # Asl kontrollerdagi kabi: create() joriy foydalanuvchi/scope bilan ishlamaydi.
    return await service.create_contract(db, dto)


@router.put("/{contract_id}", dependencies=[Depends(require_permissions("contracts.update"))])
async def update_contract(contract_id: str, dto: UpdateContractRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.update_contract(db, contract_id, dto, user)


@router.delete("/{contract_id}", dependencies=[Depends(require_permissions("contracts.delete"))])
async def remove_contract(contract_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.remove_contract(db, contract_id, user)
