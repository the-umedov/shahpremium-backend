from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status

from app.core.cookies import ACCESS_COOKIE
from app.core.database import DbSession  # noqa: F401  — re-exported for modules importing it from here
from app.core.security import AuthUser, decode_access_token, payload_to_auth_user


async def get_current_user(request: Request) -> AuthUser:
    """Global auth chegarasi ekvivalenti: cookie (web) yoki Bearer header (mobil)."""
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer ") :]
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Autentifikatsiya talab qilinadi")
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token yaroqsiz yoki muddati tugagan") from exc
    return payload_to_auth_user(payload)


CurrentUser = Annotated[AuthUser, Depends(get_current_user)]


def require_permissions(*permissions: str) -> Callable:
    """RequirePermissions + PermissionsGuard ekvivalenti.

    "<resource>.manage" shu resurs boʻyicha barcha amallarni qamraydi.
    """

    async def dependency(user: CurrentUser) -> AuthUser:
        granted = set(user.permissions)
        for perm in permissions:
            if perm in granted:
                continue
            resource = perm.split(".")[0]
            if f"{resource}.manage" in granted:
                continue
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Ruxsat yetarli emas")
        return user

    return dependency
