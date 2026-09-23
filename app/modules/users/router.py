from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.core.pagination import PaginationQuery, build_page, to_paginated
from app.models.models import User, UserRole
from app.modules.users.schemas import SetRolesRequest, UserUpdateRequest

router = APIRouter(tags=["users"])


def _serialize(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "type": user.type,
        "is_active": user.is_active,
        "profile": (
            {
                "first_name": user.profile.first_name,
                "last_name": user.profile.last_name,
            }
            if user.profile
            else None
        ),
        "region": {"id": user.region.id, "name": user.region.name} if user.region else None,
        "roles": [{"key": ur.role.key, "name": ur.role.name} for ur in user.roles],
    }


@router.get("", dependencies=[Depends(require_permissions("users.read"))])
async def list_users(db: DbSession, query: PaginationQuery = Depends()) -> dict:
    page_info = build_page(query, default_sort="created_at")
    stmt = select(User).options(
        selectinload(User.profile),
        selectinload(User.region),
        selectinload(User.roles).selectinload(UserRole.role),
    )
    count_stmt = select(func.count()).select_from(User)
    if query.search:
        stmt = stmt.where(User.email.ilike(f"%{query.search}%"))
        count_stmt = count_stmt.where(User.email.ilike(f"%{query.search}%"))

    total = (await db.execute(count_stmt)).scalar_one()
    rows = (
        await db.execute(
            stmt.order_by(getattr(User, page_info["sort"], User.created_at).desc() if page_info["order"] == "desc" else getattr(User, page_info["sort"], User.created_at).asc())
            .offset(page_info["skip"])
            .limit(page_info["take"])
        )
    ).scalars().all()

    return to_paginated([_serialize(u) for u in rows], total, page_info["page"], page_info["limit"])


@router.put("/{user_id}", dependencies=[Depends(require_permissions("users.update"))])
async def update_user(user_id: str, dto: UserUpdateRequest, db: DbSession) -> dict:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    for field, value in dto.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    return {"id": user.id}


@router.put("/{user_id}/roles", dependencies=[Depends(require_permissions("users.update"))])
async def set_roles(user_id: str, dto: SetRolesRequest, db: DbSession) -> dict:
    await db.execute(delete(UserRole).where(UserRole.user_id == user_id))
    for role_id in dto.role_ids:
        db.add(UserRole(user_id=user_id, role_id=role_id))
    await db.commit()
    return {"ok": True}
