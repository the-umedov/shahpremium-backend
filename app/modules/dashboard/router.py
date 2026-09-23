"""dashboard.controller.js ekvivalenti."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.modules.dashboard import service
from app.modules.dashboard.schemas import DashboardOverview

router = APIRouter(tags=["dashboard"])


@router.get("", response_model=DashboardOverview, dependencies=[Depends(require_permissions("dashboard.read"))])
async def get_overview(db: DbSession) -> DashboardOverview:
    return await service.overview(db)
