from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.modules.audit import service
from app.modules.audit.schemas import AuditLogQuery

router = APIRouter(tags=["audit"], dependencies=[Depends(require_permissions("audit.read"))])


# audit.read — oddiy foydalanuvchilar ko'ra olmaydi
@router.get("")
async def list_audit_logs(db: DbSession, query: AuditLogQuery = Depends()) -> dict:
    return await service.list_audit_logs(db, query)
