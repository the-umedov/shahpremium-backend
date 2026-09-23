from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.clients import service
from app.modules.clients.schemas import (
    ClientQuery,
    CreateClientRequest,
    TimelineNoteRequest,
    UpdateClientRequest,
)

router = APIRouter(tags=["clients"])


@router.get("", dependencies=[Depends(require_permissions("clients.read"))])
async def list_clients(db: DbSession, user: CurrentUser, query: ClientQuery = Depends()) -> dict:
    return await service.list_clients(db, query, user)


@router.get("/{client_id}", dependencies=[Depends(require_permissions("clients.read"))])
async def get_client(client_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.get_client(db, client_id, user)


@router.post("", status_code=201, dependencies=[Depends(require_permissions("clients.create"))])
async def create_client(dto: CreateClientRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.create_client(db, dto, user)


@router.put("/{client_id}", dependencies=[Depends(require_permissions("clients.update"))])
async def update_client(client_id: str, dto: UpdateClientRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.update_client(db, client_id, dto, user)


@router.delete("/{client_id}", dependencies=[Depends(require_permissions("clients.delete"))])
async def remove_client(client_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.remove_client(db, client_id, user)


@router.post("/{client_id}/timeline", status_code=201, dependencies=[Depends(require_permissions("clients.update"))])
async def add_note(client_id: str, dto: TimelineNoteRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.add_note(db, client_id, dto, user)
