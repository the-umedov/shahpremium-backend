"""payments.service.js ekvivalenti."""

from __future__ import annotations

from datetime import datetime
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import to_paginated
from app.core.rbac import object_access
from app.core.security import AuthUser
from app.models.enums import PaymentCategory, PaymentDirection, PaymentMethod, PaymentStatus
from app.models.models import Case, Invoice, Payment
from app.modules.payments.providers import ChargeRequest, payment_provider
from app.modules.payments.schemas import CreatePaymentRequest, QueryPaymentParams


def _page_bounds(page: int | None, limit: int | None) -> tuple[int, int, int, int]:
    """paginate.js#buildPage ekvivalenti."""
    p = max(1, page or 1)
    lim = min(100, max(1, limit or 20))
    return (p - 1) * lim, lim, p, lim


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _apply_scope(stmt: Select, user: AuthUser) -> Select:
    """Umumiy object-access scoping (common/rbac/object-access.js) — payments ham
    case/contract kabi mijozga (client) qarab cheklanadi (CLIENT roli -> faqat
    o'z clientId'si; xodim/advokat -> o'z ofisi doirasidagi ishlar orqali)."""
    scope = object_access.scope_by_client(user)
    if "client_id" in scope:
        return stmt.where(Payment.client_id == scope["client_id"])
    if "case" in scope:
        office_id = scope["case"]["office_id"]
        return stmt.join(Case, Payment.case_id == Case.id).where(Case.office_id == office_id)
    return stmt


def _serialize(payment: Payment) -> dict:
    return {
        "id": payment.id,
        "client_id": payment.client_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "direction": payment.direction,
        "category": payment.category,
        "method": payment.method,
        "case_id": payment.case_id,
        "contract_id": payment.contract_id,
        "invoice_id": payment.invoice_id,
        "comment": payment.comment,
        "status": payment.status,
        "provider_ref": payment.provider_ref,
        "paid_at": payment.paid_at,
        "created_at": payment.created_at,
        "client": (
            {"id": payment.client.id, "full_name": payment.client.full_name} if payment.client else None
        ),
    }


def _serialize_detail(payment: Payment) -> dict:
    data = _serialize(payment)
    data["case"] = (
        {"id": payment.case.id, "number": payment.case.number, "title": payment.case.title}
        if payment.case
        else None
    )
    data["contract"] = (
        {"id": payment.contract.id, "number": payment.contract.number} if payment.contract else None
    )
    data["invoice"] = (
        {
            "id": payment.invoice.id,
            "number": payment.invoice.number,
            "status": payment.invoice.status,
            "client_id": payment.invoice.client_id,
            "case_id": payment.invoice.case_id,
            "amount": payment.invoice.amount,
            "currency": payment.invoice.currency,
            "due_date": payment.invoice.due_date,
            "issued_at": payment.invoice.issued_at,
        }
        if payment.invoice
        else None
    )
    return data


async def _fetch_serialized(db: AsyncSession, payment_id: str) -> dict:
    stmt = select(Payment).options(selectinload(Payment.client)).where(Payment.id == payment_id)
    payment = (await db.execute(stmt)).scalar_one()
    return _serialize(payment)


async def list_payments(db: AsyncSession, query: QueryPaymentParams, user: AuthUser) -> dict:
    skip, take, page, limit = _page_bounds(query.page, query.limit)

    stmt = select(Payment).where(Payment.deleted_at.is_(None))
    count_stmt = select(func.count()).select_from(Payment).where(Payment.deleted_at.is_(None))
    stmt = _apply_scope(stmt, user)
    count_stmt = _apply_scope(count_stmt, user)

    if query.direction:
        stmt = stmt.where(Payment.direction == query.direction)
        count_stmt = count_stmt.where(Payment.direction == query.direction)
    if query.status:
        stmt = stmt.where(Payment.status == query.status)
        count_stmt = count_stmt.where(Payment.status == query.status)
    if query.category:
        stmt = stmt.where(Payment.category == query.category)
        count_stmt = count_stmt.where(Payment.category == query.category)
    if query.client_id and not object_access.is_client(user):
        stmt = stmt.where(Payment.client_id == query.client_id)
        count_stmt = count_stmt.where(Payment.client_id == query.client_id)
    if query.case_id:
        stmt = stmt.where(Payment.case_id == query.case_id)
        count_stmt = count_stmt.where(Payment.case_id == query.case_id)
    if query.date_from:
        gte = _parse_date(query.date_from)
        stmt = stmt.where(Payment.created_at >= gte)
        count_stmt = count_stmt.where(Payment.created_at >= gte)
    if query.date_to:
        lte = _parse_date(query.date_to)
        stmt = stmt.where(Payment.created_at <= lte)
        count_stmt = count_stmt.where(Payment.created_at <= lte)

    total = (await db.execute(count_stmt)).scalar_one()
    rows = (
        (
            await db.execute(
                stmt.options(selectinload(Payment.client))
                .order_by(Payment.created_at.desc())
                .offset(skip)
                .limit(take)
            )
        )
        .scalars()
        .all()
    )

    return to_paginated([_serialize(p) for p in rows], total, page, limit)


async def create_payment(db: AsyncSession, dto: CreatePaymentRequest) -> dict:
    payment = Payment(
        client_id=dto.client_id,
        amount=dto.amount,
        currency=dto.currency or "UZS",
        direction=dto.direction or PaymentDirection.INCOME,
        # Model ustunida category NOT NULL, lekin DTO'da ixtiyoriy — asl
        # schema.prisma topilmagani uchun berilmasa OTHER'ga tushamiz.
        category=dto.category or PaymentCategory.OTHER,
        method=dto.method,
        case_id=dto.case_id,
        contract_id=dto.contract_id,
        invoice_id=dto.invoice_id,
        comment=dto.comment,
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    await db.flush()

    # Onlayn to'lov — provider orqali (karta ma'lumoti bu yerda emas)
    if dto.method == PaymentMethod.ONLINE:
        charge = await payment_provider.create_charge(
            ChargeRequest(amount=float(dto.amount), currency=payment.currency, reference=payment.id)
        )
        payment.provider_ref = charge.provider_ref

    await db.commit()
    return await _fetch_serialized(db, payment.id)


async def _get_raw(db: AsyncSession, payment_id: str) -> Payment:
    payment = (
        await db.execute(select(Payment).where(Payment.id == payment_id, Payment.deleted_at.is_(None)))
    ).scalar_one_or_none()
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "To'lov topilmadi")
    return payment


async def update_payment_status(db: AsyncSession, payment_id: str, new_status: PaymentStatus) -> dict:
    payment = await _get_raw(db, payment_id)
    payment.status = new_status
    if new_status == PaymentStatus.PAID:
        payment.paid_at = utcnow()
    await db.commit()
    return await _fetch_serialized(db, payment_id)


async def refund_payment(db: AsyncSession, payment_id: str) -> dict:
    payment = await _get_raw(db, payment_id)
    if payment.provider_ref:
        await payment_provider.refund(payment.provider_ref)
    payment.status = PaymentStatus.REFUNDED
    await db.commit()
    return await _fetch_serialized(db, payment_id)


async def payments_summary(
    db: AsyncSession,
    date_from: str | None,
    date_to: str | None,
    client_id: str | None,
) -> dict:
    """Moliyaviy xulosa — barcha hisob-kitob backend'da."""
    conditions = [Payment.deleted_at.is_(None)]
    if client_id:
        conditions.append(Payment.client_id == client_id)
    if date_from:
        conditions.append(Payment.created_at >= _parse_date(date_from))
    if date_to:
        conditions.append(Payment.created_at <= _parse_date(date_to))

    income = (
        await db.execute(
            select(func.sum(Payment.amount)).where(
                *conditions, Payment.direction == PaymentDirection.INCOME, Payment.status == PaymentStatus.PAID
            )
        )
    ).scalar() or 0
    expense = (
        await db.execute(
            select(func.sum(Payment.amount)).where(
                *conditions, Payment.direction == PaymentDirection.EXPENSE, Payment.status == PaymentStatus.PAID
            )
        )
    ).scalar() or 0
    refunded = (
        await db.execute(select(func.sum(Payment.amount)).where(*conditions, Payment.status == PaymentStatus.REFUNDED))
    ).scalar() or 0

    invoice_conditions = [Invoice.deleted_at.is_(None)]
    if client_id:
        invoice_conditions.append(Invoice.client_id == client_id)
    invoiced = (await db.execute(select(func.sum(Invoice.amount)).where(*invoice_conditions))).scalar() or 0
    # Original kodda "paidAgg" income bilan bir xil so'rov (nusxa/xato ko'rinadi) —
    # ushbu duplikatsiya atayin saqlab qolindi (asl xulq bilan bir xil natija uchun).
    paid = income

    total_income = float(income)
    total_expense = float(expense)
    return {
        "income": total_income,
        "expense": total_expense,
        "refunded": float(refunded),
        "profit": total_income - total_expense,
        "debt": max(0.0, float(invoiced) - float(paid)),  # задолженность
    }


async def get_payment(db: AsyncSession, payment_id: str, user: AuthUser) -> dict:
    stmt = (
        select(Payment)
        .options(
            selectinload(Payment.client),
            selectinload(Payment.case),
            selectinload(Payment.contract),
            selectinload(Payment.invoice),
        )
        .where(Payment.id == payment_id, Payment.deleted_at.is_(None))
    )
    stmt = _apply_scope(stmt, user)
    payment = (await db.execute(stmt)).scalar_one_or_none()
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "To'lov topilmadi")
    return _serialize_detail(payment)
