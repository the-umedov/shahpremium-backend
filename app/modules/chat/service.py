from __future__ import annotations

from datetime import datetime
from app.core.timeutils import utcnow
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import AuthUser
from app.core.storage import storage_service
from app.models.enums import ChatType, RoleKey
from app.models.models import Chat, ChatMember, Message, User
from app.modules.chat.schemas import CreateChatRequest


def is_client(user: AuthUser) -> bool:
    return RoleKey.CLIENT.value in user.roles


def _serialize_profile(user: User | None) -> dict | None:
    if user is None or user.profile is None:
        return None
    return {"first_name": user.profile.first_name, "last_name": user.profile.last_name}


def _serialize_message(message: Message) -> dict:
    return {
        "id": message.id,
        "created_at": message.created_at,
        "chat_id": message.chat_id,
        "sender_id": message.sender_id,
        "sender": {"id": message.sender.id, "profile": _serialize_profile(message.sender)}
        if message.sender
        else None,
        "body": message.body,
        "attachment_storage_key": message.attachment_storage_key,
        "attachment_name": message.attachment_name,
        "attachment_mime": message.attachment_mime,
        "edited_at": message.edited_at,
        "deleted_at": message.deleted_at,
    }


async def assert_member(db: AsyncSession, chat_id: str, user: AuthUser) -> ChatMember:
    member = (
        await db.execute(
            select(ChatMember)
            .options(selectinload(ChatMember.chat))
            .where(ChatMember.chat_id == chat_id, ChatMember.user_id == user.id)
        )
    ).scalar_one_or_none()
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Suhbat topilmadi")
    # Mijoz ichki (xodim) suhbatiga a'zo bo'lmasa kira olmaydi
    if member.chat.is_internal and is_client(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ruxsat yo'q")
    return member


async def create_chat(db: AsyncSession, dto: CreateChatRequest, user: AuthUser) -> dict:
    # Mijoz ichki suhbat yarata olmaydi
    if dto.is_internal and is_client(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Ichki suhbat faqat xodimlar uchun")

    member_ids = list(dict.fromkeys([user.id, *dto.member_ids]))
    chat = Chat(
        title=dto.title,
        type=dto.type or (ChatType.GROUP if len(member_ids) > 2 else ChatType.DIRECT),
        is_internal=dto.is_internal or False,
        case_id=dto.case_id,
        client_id=dto.client_id,
    )
    chat.members = [ChatMember(user_id=uid) for uid in member_ids]
    db.add(chat)
    await db.commit()
    await db.refresh(chat, attribute_names=["members"])
    return {
        "id": chat.id,
        "title": chat.title,
        "type": chat.type,
        "is_internal": chat.is_internal,
        "case_id": chat.case_id,
        "client_id": chat.client_id,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
        "members": [{"id": m.id, "user_id": m.user_id, "joined_at": m.joined_at} for m in chat.members],
    }


async def list_chats(db: AsyncSession, user: AuthUser) -> list[dict]:
    chats = (
        (
            await db.execute(
                select(Chat)
                .where(Chat.members.any(ChatMember.user_id == user.id))
                .options(
                    selectinload(Chat.members).selectinload(ChatMember.user).selectinload(User.profile),
                    selectinload(Chat.messages).selectinload(Message.sender).selectinload(User.profile),
                )
                .order_by(Chat.updated_at.desc())
            )
        )
        .scalars()
        .all()
    )

    result: list[dict] = []
    for chat in chats:
        me = next((m for m in chat.members if m.user_id == user.id), None)
        unread_stmt = select(Message).where(
            Message.chat_id == chat.id,
            Message.deleted_at.is_(None),
            Message.sender_id != user.id,
        )
        if me and me.last_read_at:
            unread_stmt = unread_stmt.where(Message.created_at > me.last_read_at)
        unread = len((await db.execute(unread_stmt)).scalars().all())
        last_message = max(chat.messages, key=lambda m: m.created_at) if chat.messages else None
        result.append(
            {
                "id": chat.id,
                "title": chat.title,
                "type": chat.type,
                "is_internal": chat.is_internal,
                "case_id": chat.case_id,
                "client_id": chat.client_id,
                "updated_at": chat.updated_at,
                "members": [
                    {
                        "id": m.id,
                        "user_id": m.user_id,
                        "user": {"id": m.user.id, "profile": _serialize_profile(m.user)} if m.user else None,
                    }
                    for m in chat.members
                ],
                "unread": unread,
                "last_message": _serialize_message(last_message) if last_message else None,
            }
        )
    return result


async def get_messages(db: AsyncSession, chat_id: str, user: AuthUser, take: int = 50) -> list[dict]:
    await assert_member(db, chat_id, user)
    messages = (
        (
            await db.execute(
                select(Message)
                .where(Message.chat_id == chat_id, Message.deleted_at.is_(None))
                .options(selectinload(Message.sender).selectinload(User.profile))
                .order_by(Message.created_at.desc())
                .limit(take)
            )
        )
        .scalars()
        .all()
    )
    return [_serialize_message(m) for m in messages]


async def send_message(
    db: AsyncSession,
    chat_id: str,
    user: AuthUser,
    body: str,
    file: UploadFile | None = None,
) -> dict:
    await assert_member(db, chat_id, user)

    attachment_key: str | None = None
    attachment_name: str | None = None
    attachment_mime: str | None = None
    if file is not None:
        data = await file.read()
        ext = Path(file.filename or "").suffix
        stored = storage_service.save(data, file.content_type or "application/octet-stream", ext)
        attachment_key = stored["storage_key"]
        attachment_name = file.filename
        attachment_mime = file.content_type

    message = Message(
        chat_id=chat_id,
        sender_id=user.id,
        body=body,
        attachment_storage_key=attachment_key,
        attachment_name=attachment_name,
        attachment_mime=attachment_mime,
    )
    db.add(message)

    chat = (await db.execute(select(Chat).where(Chat.id == chat_id))).scalar_one()
    chat.updated_at = utcnow()

    await db.commit()
    await db.refresh(message, attribute_names=["sender"])
    if message.sender:
        await db.refresh(message.sender, attribute_names=["profile"])

    payload = _serialize_message(message)

    # realtime tarqatish — modul darajasida import qilinmaydi (circular import'dan qochish uchun)
    from app.modules.chat.socket_app import sio

    await sio.emit("message", _jsonable(payload), room=f"chat:{chat_id}")
    return payload


def _jsonable(payload: dict) -> dict:
    """socket.io orqali yuborishdan oldin datetime'larni ISO-string'ga aylantiradi."""
    out = {}
    for key, value in payload.items():
        if isinstance(value, datetime):
            out[key] = value.isoformat()
        else:
            out[key] = value
    return out


async def mark_read(db: AsyncSession, chat_id: str, user: AuthUser) -> dict:
    member = await assert_member(db, chat_id, user)
    member.last_read_at = utcnow()
    await db.commit()
    return {"ok": True}


async def search(db: AsyncSession, user: AuthUser, q: str) -> list[dict]:
    stmt = (
        select(Message)
        .where(
            Message.deleted_at.is_(None),
            Message.body.ilike(f"%{q}%"),
            exists().where(ChatMember.chat_id == Message.chat_id, ChatMember.user_id == user.id),
        )
        .order_by(Message.created_at.desc())
        .limit(50)
    )
    messages = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": m.id,
            "created_at": m.created_at,
            "chat_id": m.chat_id,
            "sender_id": m.sender_id,
            "body": m.body,
            "attachment_storage_key": m.attachment_storage_key,
            "attachment_name": m.attachment_name,
            "attachment_mime": m.attachment_mime,
            "edited_at": m.edited_at,
            "deleted_at": m.deleted_at,
        }
        for m in messages
    ]


async def chat_ids_for_user(db: AsyncSession, user_id: str) -> list[str]:
    """Gateway room'larга qo'shilish uchun — foydalanuvchi suhbat id'lari."""
    rows = (await db.execute(select(ChatMember.chat_id).where(ChatMember.user_id == user_id))).all()
    return [row[0] for row in rows]
