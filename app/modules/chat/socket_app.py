"""Realtime chat gateway (socket.io) — chat.gateway.js porti.

Klient handshake.auth.token orqali JWT bilan autentifikatsiya qilinadi,
so'ng o'z suhbatlari room'larга ("chat:<chatId>") qo'shiladi. Yangi xabar
(chat/service.py#send_message) shu room'ga tarqatiladi.

MUHIM: bu modul FastAPI request-scoped DI'dan tashqarida ishlaydi, shu sababli
DbSession o'rniga app.core.database.SessionLocal bilan alohida sessiya ochiladi.
"""

from __future__ import annotations

import logging

import socketio
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.models import ChatMember

logger = logging.getLogger("ChatGateway")

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio_asgi_app = socketio.ASGIApp(sio, socketio_path="socket.io")


@sio.event
async def connect(sid: str, environ: dict, auth: dict | None = None) -> bool:
    """handleConnection porti. `False` qaytarish ulanishni rad etadi — bu
    original koddagi `client.disconnect()` bilan bir xil natijaga olib keladi."""
    token = (auth or {}).get("token")
    if not token:
        return False
    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except Exception:
        return False

    async with SessionLocal() as db:
        rows = (await db.execute(select(ChatMember.chat_id).where(ChatMember.user_id == user_id))).all()
    chat_ids = [row[0] for row in rows]

    for chat_id in chat_ids:
        await sio.enter_room(sid, f"chat:{chat_id}")
    async with sio.session(sid) as session:
        session["user_id"] = user_id
    return True


@sio.event
async def disconnect(sid: str) -> None:
    logger.debug("Chat socket disconnected: %s", sid)
