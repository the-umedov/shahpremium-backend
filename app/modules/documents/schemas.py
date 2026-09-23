from __future__ import annotations

from app.core.pagination import PaginationQuery


class DocumentQuery(PaginationQuery):
    case_id: str | None = None
    client_id: str | None = None
    contract_id: str | None = None
