"""payments.controller.js ekvivalenti."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.payments import service
from app.modules.payments.schemas import (
    CreatePaymentRequest,
    PaymentDetailOut,
    PaymentOut,
    PaymentSummaryOut,
    QueryPaymentParams,
    UpdatePaymentStatusRequest,
)

router = APIRouter(tags=["payments"])


@router.get("", dependencies=[Depends(require_permissions("payments.read"))])
async def list_payments(db: DbSession, user: CurrentUser, query: QueryPaymentParams = Depends()) -> dict:
    return await service.list_payments(db, query, user)


@router.get(
    "/summary",
    response_model=PaymentSummaryOut,
    # Diqqat: asl kodda bu endpoint boshqalardan farqli "reports.read" ruxsati bilan
    # himoyalangan, "payments.read" EMAS (payments.controller.js ~59-qator).
    dependencies=[Depends(require_permissions("reports.read"))],
)
async def payments_summary(
    db: DbSession,
    date_from: str | None = None,
    date_to: str | None = None,
    client_id: str | None = None,
) -> dict:
    return await service.payments_summary(db, date_from, date_to, client_id)


@router.get("/{payment_id}", response_model=PaymentDetailOut, dependencies=[Depends(require_permissions("payments.read"))])
async def get_payment(payment_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.get_payment(db, payment_id, user)


@router.post("", status_code=201, response_model=PaymentOut, dependencies=[Depends(require_permissions("payments.create"))])
async def create_payment(dto: CreatePaymentRequest, db: DbSession) -> dict:
    return await service.create_payment(db, dto)


@router.patch(
    "/{payment_id}/status",
    response_model=PaymentOut,
    dependencies=[Depends(require_permissions("payments.update"))],
)
async def update_payment_status(payment_id: str, dto: UpdatePaymentStatusRequest, db: DbSession) -> dict:
    return await service.update_payment_status(db, payment_id, dto.status)


@router.post(
    "/{payment_id}/refund",
    status_code=201,
    response_model=PaymentOut,
    dependencies=[Depends(require_permissions("payments.update"))],
)
async def refund_payment(payment_id: str, db: DbSession) -> dict:
    return await service.refund_payment(db, payment_id)
