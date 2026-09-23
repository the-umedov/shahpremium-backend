from __future__ import annotations

import time
from dataclasses import dataclass, field

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import get_settings

settings = get_settings()
_hasher = PasswordHasher()


@dataclass
class AuthUser:
    """JWT payloaddan tiklangan joriy foydalanuvchi (jwt.strategy.validate() ekvivalenti)."""

    id: str
    type: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    client_id: str | None = None
    region_id: str | None = None
    office_id: str | None = None


def hash_password(raw: str) -> str:
    return _hasher.hash(raw)


def verify_password(hashed: str, raw: str) -> bool:
    try:
        return _hasher.verify(hashed, raw)
    except VerifyMismatchError:
        return False


def _encode(payload: dict, secret: str, ttl_seconds: int) -> str:
    now = int(time.time())
    body = {**payload, "iat": now, "exp": now + ttl_seconds}
    return jwt.encode(body, secret, algorithm="HS256")


def create_access_token(
    *,
    sub: str,
    user_type: str,
    roles: list[str],
    permissions: list[str],
    client_id: str | None = None,
    region_id: str | None = None,
    office_id: str | None = None,
) -> str:
    return _encode(
        {
            "sub": sub,
            "type": user_type,
            "roles": roles,
            "permissions": permissions,
            "clientId": client_id,
            "regionId": region_id,
            "officeId": office_id,
        },
        settings.jwt_access_secret,
        settings.jwt_access_ttl,
    )


def create_refresh_token(*, sub: str, jti: str) -> str:
    return _encode({"sub": sub, "jti": jti}, settings.jwt_refresh_secret, settings.jwt_refresh_ttl)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_access_secret, algorithms=["HS256"])


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_refresh_secret, algorithms=["HS256"])


def payload_to_auth_user(payload: dict) -> AuthUser:
    return AuthUser(
        id=payload["sub"],
        type=payload.get("type", ""),
        roles=payload.get("roles") or [],
        permissions=payload.get("permissions") or [],
        client_id=payload.get("clientId"),
        region_id=payload.get("regionId"),
        office_id=payload.get("officeId"),
    )
