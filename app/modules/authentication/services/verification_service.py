from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from app.core.timeutils import utcnow

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import VerificationTokenType
from app.models.models import VerificationToken

TTL = timedelta(minutes=30)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


async def _persist(db: AsyncSession, user_id: str, type_: VerificationTokenType, raw: str) -> None:
    await db.execute(
        update(VerificationToken)
        .where(
            VerificationToken.user_id == user_id,
            VerificationToken.type == type_,
            VerificationToken.consumed_at.is_(None),
        )
        .values(consumed_at=utcnow())
    )
    db.add(
        VerificationToken(
            user_id=user_id,
            type=type_,
            token_hash=_hash(raw),
            expires_at=utcnow() + TTL,
        )
    )
    await db.commit()


async def create_token(db: AsyncSession, user_id: str, type_: VerificationTokenType) -> str:
    """Uzun tasodifiy token (email havolalari uchun)."""
    raw = secrets.token_urlsafe(24)
    await _persist(db, user_id, type_, raw)
    return raw


async def create_code(db: AsyncSession, user_id: str, type_: VerificationTokenType) -> str:
    """6 xonali raqamli kod (SMS/OTP uchun)."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    await _persist(db, user_id, type_, code)
    return code


async def consume(db: AsyncSession, type_: VerificationTokenType, raw: str, user_id: str | None = None) -> dict | None:
    """Tokenni tekshiradi va isteʼmol qiladi (bir marta ishlatiladi)."""
    token_hash = _hash(raw)
    query = select(VerificationToken).where(
        VerificationToken.type == type_,
        VerificationToken.token_hash == token_hash,
        VerificationToken.consumed_at.is_(None),
        VerificationToken.expires_at > utcnow(),
    )
    if user_id:
        query = query.where(VerificationToken.user_id == user_id)
    token = (await db.execute(query)).scalar_one_or_none()
    if not token:
        return None
    token.consumed_at = utcnow()
    await db.commit()
    return {"user_id": token.user_id}
