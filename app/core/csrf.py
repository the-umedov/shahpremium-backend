from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.cookies import CSRF_COOKIE

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class CsrfMiddleware(BaseHTTPMiddleware):
    """CSRF himoyasi (double-submit cookie) — CsrfGuard ekvivalenti.

    Faqat cookie orqali autentifikatsiya qilingan mutatsiya soʻrovlariga qoʻllanadi.
    Bearer token (mobil) ishlatilsa — CSRF talab qilinmaydi.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method in _SAFE_METHODS:
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        cookie_token = request.cookies.get(CSRF_COOKIE)
        if not cookie_token:
            return await call_next(request)

        header_token = request.headers.get("x-csrf-token")
        if not header_token or header_token != cookie_token:
            return JSONResponse(
                {"statusCode": 403, "code": "FORBIDDEN", "message": "CSRF token mos kelmadi"},
                status_code=403,
            )
        return await call_next(request)
