from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from http import HTTPStatus


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    body = {
        "statusCode": exc.status_code,
        "code": HTTPStatus(exc.status_code).phrase.upper().replace(" ", "_"),
        "message": exc.detail,
        "requestId": request.headers.get("x-request-id"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(body, status_code=exc.status_code, headers=getattr(exc, "headers", None))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    body = {
        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "code": "INTERNAL_SERVER_ERROR",
        "message": "Ichki server xatosi",
        "requestId": request.headers.get("x-request-id"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return JSONResponse(body, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
