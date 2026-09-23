from __future__ import annotations

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.cookies import ACCESS_COOKIE
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.models import AuditLog

_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Har bir oʻzgartiruvchi soʻrovni audit_logs ga yozadi (AuditInterceptor ekvivalenti).

    Asinxron/best-effort — audit yozuvi asosiy oqimni buzmasin.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.method not in _MUTATING:
            return response

        actor_id = None
        token = request.cookies.get(ACCESS_COOKIE)
        if not token:
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[len("Bearer ") :]
        if token:
            try:
                actor_id = decode_access_token(token).get("sub")
            except jwt.PyJWTError:
                actor_id = None

        route = request.scope.get("route")
        action = f"{route.name}" if route else request.url.path
        entity = request.url.path.strip("/").split("/")[0] if request.url.path else "unknown"

        try:
            async with SessionLocal() as session:
                session.add(
                    AuditLog(
                        actor_id=actor_id,
                        action=action,
                        entity=entity,
                        ip=request.client.host if request.client else None,
                        request_id=request.headers.get("x-request-id"),
                    )
                )
                await session.commit()
        except Exception:
            pass  # audit yozuvi asosiy oqimni buzmasin

        return response
