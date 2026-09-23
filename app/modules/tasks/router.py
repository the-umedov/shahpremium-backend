"""tasks.controller.js ekvivalenti."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.tasks import service
from app.modules.tasks.schemas import CreateTaskRequest, MoveTaskRequest, TaskQuery, UpdateTaskRequest

router = APIRouter(tags=["tasks"])


@router.get("", dependencies=[Depends(require_permissions("tasks.read"))])
async def list_tasks(db: DbSession, user: CurrentUser, query: TaskQuery = Depends()) -> dict:
    return await service.list_tasks(db, query, user)


# Kanban board
@router.get("/board", dependencies=[Depends(require_permissions("tasks.read"))])
async def get_board(db: DbSession, user: CurrentUser, case_id: str | None = Query(None)) -> dict:
    return await service.board(db, user, case_id)


# Muddatlarni skanerlash (overdue + bildirishnoma) — boshqaruv
@router.post("/scan-deadlines", status_code=201, dependencies=[Depends(require_permissions("tasks.update"))])
async def scan_deadlines(db: DbSession) -> dict:
    return await service.scan_deadlines(db)


@router.post("", status_code=201, dependencies=[Depends(require_permissions("tasks.create"))])
async def create_task(dto: CreateTaskRequest, db: DbSession, user: CurrentUser) -> dict:
    task = await service.create(db, dto, user)
    return service.serialize(task)


@router.put("/{id}", dependencies=[Depends(require_permissions("tasks.update"))])
async def update_task(id: str, dto: UpdateTaskRequest, db: DbSession, user: CurrentUser) -> dict:
    task = await service.update(db, id, dto, user)
    return service.serialize(task)


@router.patch("/{id}/move", dependencies=[Depends(require_permissions("tasks.update"))])
async def move_task(id: str, dto: MoveTaskRequest, db: DbSession, user: CurrentUser) -> dict:
    task = await service.move(db, id, dto.status, user)
    return service.serialize(task)


@router.delete("/{id}", dependencies=[Depends(require_permissions("tasks.delete"))])
async def remove_task(id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.remove(db, id, user)
