from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.models.models import Permission

router = APIRouter(tags=["permissions"])


@router.get("", dependencies=[Depends(require_permissions("roles.manage"))])
async def list_permissions(db: DbSession) -> list[dict]:
    rows = (
        await db.execute(select(Permission).order_by(Permission.resource.asc(), Permission.action.asc()))
    ).scalars().all()
    return [
        {"id": p.id, "key": p.key, "resource": p.resource, "action": p.action, "description": p.description}
        for p in rows
    ]
