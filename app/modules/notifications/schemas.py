from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.core.pagination import PaginationQuery
from app.models.enums import NotificationChannel


class NotificationListQuery(PaginationQuery):
    unread_only: str | None = None  # "true" bo'lsa faqat o'qilmaganlar (Nest DTO'ga mos)


class NotificationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    created_at: datetime
    user_id: str
    event: str | None
    channel: NotificationChannel
    title: str
    body: str
    is_read: bool
    read_at: datetime | None
    sent_at: datetime | None


class DispatchRequest(BaseModel):
    """notifications.service.js#dispatch parametrlari — boshqa modullar ichki chaqiradi."""

    user_id: str
    event: str
    title: str
    body: str
