from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SettingUpsertRequest(BaseModel):
    key: str
    value: Any
    scope: str | None = None


class PreferenceUpdateRequest(BaseModel):
    """preferences.controller.js#update: dto to'liq ixtiyoriy maydonlar (upsert)."""

    locale: str | None = None
    theme: str | None = None
    timezone: str | None = None
    date_format: str | None = None
    notify_in_app: bool | None = None
    notify_email: bool | None = None
    notify_sms: bool | None = None
    notify_push: bool | None = None
