import re

from pydantic import BaseModel, field_validator

_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,49}$")


class CreateRoleRequest(BaseModel):
    key: str
    name: str
    description: str | None = None
    permission_ids: list[str] = []

    @field_validator("key")
    @classmethod
    def _validate_key(cls, v: str) -> str:
        v = v.strip().upper().replace(" ", "_")
        if not _KEY_RE.match(v):
            raise ValueError(
                "Kalit faqat lotin harflar (A-Z), raqam va pastki chiziqdan iborat bo'lsin, harf bilan boshlansin"
            )
        return v


class UpdateRoleRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    permission_ids: list[str] | None = None
