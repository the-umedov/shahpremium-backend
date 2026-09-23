from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.modules.offices.schemas import OfficeCreateRequest, OfficeUpdateRequest
from app.modules.offices.service import create_office, list_offices, remove_office, update_office

router = APIRouter(tags=["offices"])


@router.get("")
async def list_offices_route(db: DbSession) -> list[dict]:
    return await list_offices(db)


@router.post("", status_code=201, dependencies=[Depends(require_permissions("offices.manage"))])
async def create_office_route(dto: OfficeCreateRequest, db: DbSession) -> dict:
    return await create_office(db, dto)


@router.put("/{office_id}", dependencies=[Depends(require_permissions("offices.manage"))])
async def update_office_route(office_id: str, dto: OfficeUpdateRequest, db: DbSession) -> dict:
    return await update_office(db, office_id, dto)


@router.delete("/{office_id}", dependencies=[Depends(require_permissions("offices.manage"))])
async def remove_office_route(office_id: str, db: DbSession) -> dict:
    return await remove_office(db, office_id)
