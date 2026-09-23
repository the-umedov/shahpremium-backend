from __future__ import annotations

from datetime import datetime
from app.core.timeutils import utcnow

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import build_page, model_to_dict, to_paginated
from app.core.security import AuthUser
from app.models.enums import NotificationChannel
from app.models.models import Notification, User, UserPreference
from app.modules.notifications.channels import (
    OutboundNotification,
    email_channel,
    push_channel,
    sms_channel,
)
from app.modules.notifications.schemas import NotificationListQuery


async def list_notifications(db: AsyncSession, user: AuthUser, query: NotificationListQuery) -> dict:
    page_info = build_page(query, default_sort="created_at")
    stmt = select(Notification).where(Notification.user_id == user.id)
    count_stmt = select(func.count()).select_from(Notification).where(Notification.user_id == user.id)
    if query.unread_only == "true":
        stmt = stmt.where(Notification.is_read.is_(False))
        count_stmt = count_stmt.where(Notification.is_read.is_(False))

    total = (await db.execute(count_stmt)).scalar_one()
    order_col = getattr(Notification, page_info["sort"], Notification.created_at)
    order_col = order_col.desc() if page_info["order"] == "desc" else order_col.asc()
    rows = (
        (await db.execute(stmt.order_by(order_col).offset(page_info["skip"]).limit(page_info["take"])))
        .scalars()
        .all()
    )
    return to_paginated([model_to_dict(r) for r in rows], total, page_info["page"], page_info["limit"])


async def unread_count(db: AsyncSession, user: AuthUser) -> dict:
    count = (
        await db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        )
    ).scalar_one()
    return {"count": count}


async def mark_read(db: AsyncSession, notification_id: str, user: AuthUser) -> dict:
    await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user.id)
        .values(is_read=True, read_at=utcnow())
    )
    await db.commit()
    return {"ok": True}


async def mark_all_read(db: AsyncSession, user: AuthUser) -> dict:
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True, read_at=utcnow())
    )
    await db.commit()
    return {"updated": result.rowcount or 0}


async def dispatch(db: AsyncSession, *, user_id: str, event: str, title: str, body: str) -> dict:
    """Bildirishnoma yuborish — in-app doim yoziladi; email/SMS/push
    foydalanuvchi sozlamalariga qarab (arxitektura tayyor).
    """
    pref = (
        await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
    ).scalar_one_or_none()
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()

    # in-app
    if pref.notify_in_app if pref is not None else True:
        db.add(
            Notification(
                user_id=user_id,
                channel=NotificationChannel.IN_APP,
                event=event,
                title=title,
                body=body,
            )
        )
        await db.commit()

    # email
    if pref and pref.notify_email and user and user.email:
        await email_channel.send(OutboundNotification(to=user.email, title=title, body=body))

    # sms
    if pref and pref.notify_sms and user and user.phone:
        await sms_channel.send(OutboundNotification(to=user.phone, title=title, body=body))

    # push
    if pref and pref.notify_push:
        await push_channel.send(OutboundNotification(to=user_id, title=title, body=body))

    return {"ok": True}
