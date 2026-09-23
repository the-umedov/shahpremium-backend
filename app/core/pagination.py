from typing import Generic, Literal, TypeVar

from pydantic import BaseModel
from sqlalchemy import inspect

T = TypeVar("T")


def model_to_dict(obj) -> dict:
    """SQLAlchemy ORM qatorini Python-tomon snake_case atribut nomlari bilan
    dict'ga aylantiradi (DB ustun nomi bilan EMAS — ular haqiqiy Prisma
    camelCase nomlariga mos bo'lishi mumkin, masalan "createdAt")."""
    return {attr.key: getattr(obj, attr.key) for attr in inspect(obj).mapper.column_attrs}


class PaginationQuery(BaseModel):
    page: int = 1
    limit: int = 20
    sort: str | None = None
    order: Literal["asc", "desc"] = "desc"
    search: str | None = None


class PageMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


def build_page(query: PaginationQuery, default_sort: str = "created_at") -> dict:
    page = max(1, query.page or 1)
    limit = min(100, max(1, query.limit or 20))
    return {
        "skip": (page - 1) * limit,
        "take": limit,
        "sort": query.sort or default_sort,
        "order": query.order or "desc",
        "page": page,
        "limit": limit,
    }


def to_paginated(items: list, total: int, page: int, limit: int) -> dict:
    return {
        "items": items,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": max(1, -(-total // limit)),
        },
    }
