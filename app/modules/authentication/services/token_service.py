from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.models import RefreshToken

settings = get_settings()


@dataclass
class RequestMeta:
    ip: str | None = None
    user_agent: str | None = None
    label: str | None = None
    request_id: str | None = None


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def sign_access_token(claims: dict) -> str:
    return create_access_token(
        sub=claims["sub"],
        user_type=claims["type"],
        roles=claims["roles"],
        permissions=claims["permissions"],
        client_id=claims.get("clientId"),
        region_id=claims.get("regionId"),
        office_id=claims.get("officeId"),
    )


async def issue_refresh_session(db: AsyncSession, user_id: str, meta: RequestMeta) -> dict:
    """Yangi refresh sessiyasi yaratadi (yangi family)."""
    raw = secrets.token_urlsafe(36)
    family_id = str(uuid.uuid4())
    session = RefreshToken(
        user_id=user_id,
        token_hash=_sha256(raw),
        family_id=family_id,
        ip=meta.ip,
        user_agent=meta.user_agent,
        label=meta.label,
        expires_at=utcnow() + timedelta(seconds=settings.jwt_refresh_ttl),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"token": f"{session.id}.{raw}", "session_id": session.id}


async def rotate_refresh_token(db: AsyncSession, presented: str, meta: RequestMeta) -> dict:
    """Refresh token rotatsiyasi: REUSE aniqlansa butun family bekor qilinadi."""
    try:
        session_id, raw = presented.split(".", 1)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Notoʻgʻri token")
    if not session_id or not raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Notoʻgʻri token")

    current = (await db.execute(select(RefreshToken).where(RefreshToken.id == session_id))).scalar_one_or_none()
    if not current:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessiya topilmadi")

    presented_hash = _sha256(raw)
    if current.revoked_at is not None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == current.family_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=utcnow())
        )
        await db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token qayta ishlatildi — sessiya bekor qilindi")

    if current.token_hash != presented_hash:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token mos kelmadi")

    if current.expires_at < utcnow():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessiya muddati tugagan")

    raw2 = secrets.token_urlsafe(36)
    next_session = RefreshToken(
        user_id=current.user_id,
        token_hash=_sha256(raw2),
        family_id=current.family_id,
        ip=meta.ip,
        user_agent=meta.user_agent,
        label=meta.label or current.label,
        expires_at=utcnow() + timedelta(seconds=settings.jwt_refresh_ttl),
    )
    db.add(next_session)
    await db.flush()

    current.revoked_at = utcnow()
    current.replaced_by_hash = next_session.token_hash
    current.last_used_at = utcnow()
    await db.commit()
    await db.refresh(next_session)

    return {"user_id": current.user_id, "token": f"{next_session.id}.{raw2}", "session_id": next_session.id}


async def revoke_session(db: AsyncSession, session_id: str) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == session_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    await db.commit()


async def revoke_all_except(db: AsyncSession, user_id: str, keep_session_id: str | None) -> int:
    """Berilgan sessiyadan tashqari barcha faol sessiyalarni bekor qiladi."""
    stmt = update(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
    if keep_session_id:
        stmt = stmt.where(RefreshToken.id != keep_session_id)
    stmt = stmt.values(revoked_at=utcnow())
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
