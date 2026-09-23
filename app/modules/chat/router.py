from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.database import DbSession
from app.core.deps import CurrentUser, require_permissions
from app.modules.chat import service
from app.modules.chat.schemas import CreateChatRequest

router = APIRouter(tags=["chat"], dependencies=[Depends(require_permissions("chat.use"))])


@router.get("")
async def list_chats(db: DbSession, user: CurrentUser) -> list[dict]:
    return await service.list_chats(db, user)


@router.get("/search")
async def search(db: DbSession, user: CurrentUser, q: str = "") -> list[dict]:
    return await service.search(db, user, q or "")


@router.post("")
async def create_chat(dto: CreateChatRequest, db: DbSession, user: CurrentUser) -> dict:
    return await service.create_chat(db, dto, user)


@router.get("/{chat_id}/messages")
async def messages(chat_id: str, db: DbSession, user: CurrentUser) -> list[dict]:
    return await service.get_messages(db, chat_id, user)


@router.post("/{chat_id}/messages")
async def send(
    chat_id: str,
    db: DbSession,
    user: CurrentUser,
    body: str = Form(...),
    file: UploadFile | None = File(None),
) -> dict:
    return await service.send_message(db, chat_id, user, body, file)


@router.post("/{chat_id}/read")
async def read(chat_id: str, db: DbSession, user: CurrentUser) -> dict:
    return await service.mark_read(db, chat_id, user)
