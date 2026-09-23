from fastapi import APIRouter, Depends, Query

from app.core.database import DbSession
from app.core.deps import require_permissions
from app.core.pagination import PaginationQuery
from app.models.enums import ServiceCategory
from app.modules.services.schemas import (
    ReorderRequest,
    ServiceCreateRequest,
    ServiceUpdateRequest,
    SetActiveRequest,
)
from app.modules.services.service import (
    create_service,
    get_service_dict,
    list_services,
    reorder_services,
    set_active,
    update_service,
)

router = APIRouter(tags=["services"])


# Ro'yxat/karta — har qanday autentifikatsiyalangan foydalanuvchi uchun ochiq
# (asl kodda RequirePermissions yo'q, faqat global JwtAuthGuard bor).
@router.get("")
async def list_services_route(
    db: DbSession,
    query: PaginationQuery = Depends(),
    category: ServiceCategory | None = Query(None),
    active: str | None = Query(None),
) -> dict:
    return await list_services(db, query, category, active)


@router.get("/{service_id}")
async def get_service_route(service_id: str, db: DbSession) -> dict:
    return await get_service_dict(db, service_id)


@router.post("", status_code=201, dependencies=[Depends(require_permissions("services.manage"))])
async def create_service_route(dto: ServiceCreateRequest, db: DbSession) -> dict:
    return await create_service(db, dto)


@router.put("/{service_id}", dependencies=[Depends(require_permissions("services.manage"))])
async def update_service_route(service_id: str, dto: ServiceUpdateRequest, db: DbSession) -> dict:
    return await update_service(db, service_id, dto)


@router.patch("/{service_id}/active", dependencies=[Depends(require_permissions("services.manage"))])
async def set_service_active_route(service_id: str, dto: SetActiveRequest, db: DbSession) -> dict:
    return await set_active(db, service_id, dto.is_active)


@router.patch("/reorder", dependencies=[Depends(require_permissions("services.manage"))])
async def reorder_services_route(dto: ReorderRequest, db: DbSession) -> dict:
    return await reorder_services(db, dto.items)
