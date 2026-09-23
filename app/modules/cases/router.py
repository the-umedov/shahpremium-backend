from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.cases import service
from app.modules.cases.schemas import CaseNoteRequest, CaseQuery, CreateCaseRequest, UpdateCaseRequest

router = APIRouter(tags=["cases"])


@router.get("", dependencies=[Depends(require_permissions("cases.read"))])
async def list_cases(db: DbSession, user: CurrentUser, query: CaseQuery = Depends()) -> dict:
    return await service.list_cases(db, query, user)


@router.get("/{case_id}", dependencies=[Depends(require_permissions("cases.read"))])
async def get_case(case_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.get_case(db, case_id, user)


@router.post("", status_code=201, dependencies=[Depends(require_permissions("cases.create"))])
async def create_case(dto: CreateCaseRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.create_case(db, dto, user)


@router.put("/{case_id}", dependencies=[Depends(require_permissions("cases.update"))])
async def update_case(case_id: str, dto: UpdateCaseRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.update_case(db, case_id, dto, user)


@router.delete("/{case_id}", dependencies=[Depends(require_permissions("cases.delete"))])
async def remove_case(case_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.remove_case(db, case_id, user)


@router.post("/{case_id}/notes", status_code=201, dependencies=[Depends(require_permissions("cases.update"))])
async def add_note(case_id: str, dto: CaseNoteRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.add_note(db, case_id, dto, user)
