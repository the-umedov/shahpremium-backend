from __future__ import annotations

from app.core.pagination import PaginationQuery


class AuditLogQuery(PaginationQuery):
    limit: int = 30  # audit.service.js: query.limit ?? 30 (boshqa modullarda odatda 20)
    actor_id: str | None = None
    entity: str | None = None
    action: str | None = None
    date_from: str | None = None
    date_to: str | None = None
