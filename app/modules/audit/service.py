from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import build_page, model_to_dict, to_paginated
from app.models.models import AuditLog
from app.modules.audit.schemas import AuditLogQuery


# Audit log FAQAT o'qiladi — tahrirlash/o'chirish endpointi yo'q (append-only).
async def list_audit_logs(db: AsyncSession, query: AuditLogQuery) -> dict:
    page_info = build_page(query, default_sort="created_at")

    stmt = select(AuditLog)
    count_stmt = select(func.count()).select_from(AuditLog)

    if query.actor_id:
        stmt = stmt.where(AuditLog.actor_id == query.actor_id)
        count_stmt = count_stmt.where(AuditLog.actor_id == query.actor_id)
    if query.entity:
        stmt = stmt.where(AuditLog.entity == query.entity)
        count_stmt = count_stmt.where(AuditLog.entity == query.entity)
    if query.action:
        stmt = stmt.where(AuditLog.action.ilike(f"%{query.action}%"))
        count_stmt = count_stmt.where(AuditLog.action.ilike(f"%{query.action}%"))
    if query.date_from:
        gte = datetime.fromisoformat(query.date_from)
        stmt = stmt.where(AuditLog.created_at >= gte)
        count_stmt = count_stmt.where(AuditLog.created_at >= gte)
    if query.date_to:
        lte = datetime.fromisoformat(query.date_to)
        stmt = stmt.where(AuditLog.created_at <= lte)
        count_stmt = count_stmt.where(AuditLog.created_at <= lte)

    total = (await db.execute(count_stmt)).scalar_one()
    order_col = getattr(AuditLog, page_info["sort"], AuditLog.created_at)
    order_col = order_col.desc() if page_info["order"] == "desc" else order_col.asc()
    rows = (
        (await db.execute(stmt.order_by(order_col).offset(page_info["skip"]).limit(page_info["take"])))
        .scalars()
        .all()
    )
    return to_paginated([model_to_dict(r) for r in rows], total, page_info["page"], page_info["limit"])
