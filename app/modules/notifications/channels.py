"""Bildirishnoma kanallari abstraksiyasi (channels.js portlari).

in-app to'liq ishlaydi (notifications jadvaliga yoziladi); email/SMS/push uchun
arxitektura tayyor (stub) — hozircha faqat log yoziladi. Kelajakda
SMTP/SMS-shluz/FCM bilan almashtiriladi. Maxfiy kalitlar env'da bo'ladi.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol


@dataclass
class OutboundNotification:
    to: str
    title: str
    body: str


class NotificationChannelAdapter(Protocol):
    key: str

    async def send(self, msg: OutboundNotification) -> dict: ...


class EmailChannel:
    key = "EMAIL"

    def __init__(self) -> None:
        self.logger = logging.getLogger("EmailChannel")

    async def send(self, msg: OutboundNotification) -> dict:
        # Amalga oshirishда: SMTP (SMTP_* env). Hozircha log.
        self.logger.info("[email→%s] %s", msg.to, msg.title)
        return {"ok": True}


class SmsChannel:
    key = "SMS"

    def __init__(self) -> None:
        self.logger = logging.getLogger("SmsChannel")

    async def send(self, msg: OutboundNotification) -> dict:
        self.logger.info("[sms→%s] %s", msg.to, msg.title)
        return {"ok": True}


class PushChannel:
    key = "PUSH"

    def __init__(self) -> None:
        self.logger = logging.getLogger("PushChannel")

    async def send(self, msg: OutboundNotification) -> dict:
        self.logger.info("[push→%s] %s", msg.to, msg.title)
        return {"ok": True}


email_channel = EmailChannel()
sms_channel = SmsChannel()
push_channel = PushChannel()
