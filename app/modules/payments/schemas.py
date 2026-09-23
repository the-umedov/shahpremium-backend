"""payment.dto.js ekvivalenti."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentCategory, PaymentDirection, PaymentMethod, PaymentStatus


class CreatePaymentRequest(BaseModel):
    client_id: str
    amount: Decimal = Field(ge=0)
    currency: str | None = None
    direction: PaymentDirection | None = None
    category: PaymentCategory | None = None
    method: PaymentMethod | None = None
    case_id: str | None = None
    contract_id: str | None = None
    invoice_id: str | None = None
    comment: str | None = None


class QueryPaymentParams(BaseModel):
    """QueryPaymentDto ekvivalenti — sahifalash o'z page/limit'iga ega
    (umumiy PaginationQuery'dan farqli, sort/order/search yo'q)."""

    direction: PaymentDirection | None = None
    status: PaymentStatus | None = None
    category: PaymentCategory | None = None
    client_id: str | None = None
    case_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    page: int = 1
    limit: int = 20


class UpdatePaymentStatusRequest(BaseModel):
    status: PaymentStatus


class ClientBrief(BaseModel):
    id: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class CaseBrief(BaseModel):
    id: str
    number: str
    title: str

    model_config = ConfigDict(from_attributes=True)


class ContractBrief(BaseModel):
    id: str
    number: str

    model_config = ConfigDict(from_attributes=True)


class InvoiceOut(BaseModel):
    """Invoice'ning o'z controller'i yo'q — faqat Payment orqali (include.invoice) ko'rinadi."""

    id: str
    number: str
    status: str
    client_id: str
    case_id: str | None
    amount: Decimal
    currency: str
    due_date: datetime | None
    issued_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PaymentOut(BaseModel):
    id: str
    client_id: str
    amount: Decimal
    currency: str
    direction: PaymentDirection
    category: PaymentCategory
    method: PaymentMethod | None
    case_id: str | None
    contract_id: str | None
    invoice_id: str | None
    comment: str | None
    status: PaymentStatus
    provider_ref: str | None
    paid_at: datetime | None
    created_at: datetime
    client: ClientBrief | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentDetailOut(PaymentOut):
    """get() — include: {client, case, contract, invoice}."""

    case: CaseBrief | None = None
    contract: ContractBrief | None = None
    invoice: InvoiceOut | None = None


class PaymentSummaryOut(BaseModel):
    """summary() — moliyaviy xulosa."""

    income: float
    expense: float
    refunded: float
    profit: float
    debt: float
