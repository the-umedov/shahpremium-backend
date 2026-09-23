from __future__ import annotations

from pydantic import BaseModel

from app.models.enums import ChatType


class CreateChatRequest(BaseModel):
    member_ids: list[str]
    title: str | None = None
    type: ChatType | None = None
    is_internal: bool | None = None
    case_id: str | None = None
    client_id: str | None = None


class SendMessageRequest(BaseModel):
    body: str
