from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.notifications import service
from app.modules.notifications.schemas import NotificationListQuery

router = APIRouter(
    tags=["notifications"],
    dependencies=[Depends(require_permissions("notifications.read"))],
)


@router.get("")
async def list_notifications(db: DbSession, user: CurrentUser, query: NotificationListQuery = Depends()) -> dict:
    return await service.list_notifications(db, user, query)


@router.get("/unread-count")
async def unread_count(db: DbSession, user: CurrentUser) -> dict:
    return await service.unread_count(db, user)


@router.post("/read-all")
async def read_all(db: DbSession, user: CurrentUser) -> dict:
    return await service.mark_all_read(db, user)


@router.post("/{notification_id}/read")
async def read_one(notification_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.mark_read(db, notification_id, user)
