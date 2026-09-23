"""Payment provider abstraksiyasi — kelajakdagi shluzlar (Payme, Click, ...) uchun.

MUHIM: ShahPremium karta ma'lumotlarini SAQLAMAYDI. Provider faqat
havola/referens qaytaradi; sezgir ma'lumot shluz tomonida qoladi.

Manba: apps/api/dist/modules/payments/providers/payment-provider.js (interfeys)
va providers/manual.provider.js (standart implementatsiya).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass
class ChargeRequest:
    amount: float
    currency: str
    reference: str
    description: str | None = None


@dataclass
class ChargeResult:
    provider_ref: str
    status: Literal["PENDING", "PAID", "FAILED"]
    redirect_url: str | None = None


class PaymentProvider(Protocol):
    """`PaymentProvider` interfeysi (payment-provider.d.ts) ekvivalenti."""

    name: str

    async def create_charge(self, req: ChargeRequest) -> ChargeResult: ...

    async def refund(self, provider_ref: str) -> dict: ...


class ManualPaymentProvider:
    """Standart provider — qo'lda/naqd to'lovlar uchun (shluzsiz).

    Kelajakda PaymeProvider/ClickProvider shu interfeys bilan almashtiriladi.
    """

    name = "manual"

    async def create_charge(self, req: ChargeRequest) -> ChargeResult:
        # Haqiqiy shluz yo'q — referens beramiz, holatni operator tasdiqlaydi.
        return ChargeResult(provider_ref=f"MAN-{uuid.uuid4()}", status="PENDING")

    async def refund(self, provider_ref: str) -> dict:
        return {"ok": True}


# payments.module.js'da PAYMENT_PROVIDER token orqali DI qilingan singleton ekvivalenti.
payment_provider: PaymentProvider = ManualPaymentProvider()
