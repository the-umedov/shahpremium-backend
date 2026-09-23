from fastapi import APIRouter, Depends, Query

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.core.pagination import PaginationQuery
from app.models.enums import EmployeeKind, EmployeeStatus
from app.modules.employees.schemas import (
    EmployeeUpdateRequest,
    SetCommissionRequest,
    SetScheduleRequest,
)
from app.modules.employees.service import (
    get_employee,
    list_employees,
    set_commission,
    set_schedule,
    update_employee,
)

router = APIRouter(tags=["employees"])


@router.get("", dependencies=[Depends(require_permissions("employees.read"))])
async def list_employees_route(
    db: DbSession,
    query: PaginationQuery = Depends(),
    kind: EmployeeKind | None = Query(None),
    status: EmployeeStatus | None = Query(None),
    region_id: str | None = Query(None),
) -> dict:
    return await list_employees(db, query, kind, status, region_id)


@router.get("/{employee_id}", dependencies=[Depends(require_permissions("employees.read"))])
async def get_employee_route(employee_id: str, db: DbSession) -> dict:
    return await get_employee(db, employee_id)


@router.put("/{employee_id}", dependencies=[Depends(require_permissions("employees.update"))])
async def update_employee_route(employee_id: str, dto: EmployeeUpdateRequest, db: DbSession) -> dict:
    return await update_employee(db, employee_id, dto)


# Foizli model — SUPER_ADMIN tekshiruvi service ichida
@router.patch("/{employee_id}/commission", dependencies=[Depends(require_permissions("employees.update"))])
async def set_commission_route(
    employee_id: str, dto: SetCommissionRequest, db: DbSession, user: CurrentUser
) -> dict:
    return await set_commission(db, employee_id, dto.commission_percent, user)


@router.put("/{employee_id}/schedule", dependencies=[Depends(require_permissions("employees.update"))])
async def set_schedule_route(employee_id: str, dto: SetScheduleRequest, db: DbSession) -> list[dict]:
    return await set_schedule(db, employee_id, dto.items)
