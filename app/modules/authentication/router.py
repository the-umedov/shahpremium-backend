import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.cookies import CSRF_COOKIE, REFRESH_COOKIE, clear_auth_cookies, set_auth_cookies
from app.core.database import DbSession
from app.core.deps import CurrentUser, get_current_user
from app.modules.authentication import service as auth_service
from app.modules.authentication.schemas import (
    ChangePasswordRequest,
    CsrfResponse,
    LoginRequest,
    LogoutOthersResponse,
    OkResponse,
    RegisterRequest,
    RegisterResponse,
    RequestPasswordResetRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyContactRequest,
)
from app.modules.authentication.services.token_service import RequestMeta

router = APIRouter(tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


def _ctx(request: Request) -> RequestMeta:
    ua = request.headers.get("user-agent")
    return RequestMeta(
        ip=request.client.host if request.client else None,
        user_agent=ua,
        label=ua[:80] if ua else None,
        request_id=request.headers.get("x-request-id"),
    )


def _read_refresh(request: Request) -> str | None:
    return request.cookies.get(REFRESH_COOKIE)


def _current_session_id(request: Request) -> str | None:
    rt = _read_refresh(request)
    return rt.split(".")[0] if rt else None


@router.get("/csrf", response_model=CsrfResponse)
async def csrf(response: Response) -> CsrfResponse:
    """CSRF token (cookie-auth mijozlar uchun)."""
    token = secrets.token_hex(24)
    response.set_cookie(CSRF_COOKIE, token, httponly=False, samesite="lax", path="/")
    return CsrfResponse(csrf_token=token)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(dto: RegisterRequest, request: Request, db: DbSession) -> RegisterResponse:
    result = await auth_service.register(db, dto)
    return RegisterResponse(user_id=result["user_id"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def login(dto: LoginRequest, request: Request, response: Response, db: DbSession) -> TokenResponse:
    tokens = await auth_service.login(db, dto, _ctx(request))
    set_auth_cookies(response, access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])
    return TokenResponse(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def refresh(request: Request, response: Response, db: DbSession) -> TokenResponse:
    presented = _read_refresh(request)
    if not presented:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token yoʻq")
    tokens = await auth_service.refresh(db, presented, _ctx(request))
    set_auth_cookies(response, access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])
    return TokenResponse(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])


@router.post("/logout", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def logout(
    request: Request, response: Response, db: DbSession, user: CurrentUser
) -> OkResponse:
    session_id = _current_session_id(request)
    if session_id:
        await auth_service.logout(db, session_id, user.id, _ctx(request))
    clear_auth_cookies(response)
    return OkResponse()


@router.post("/logout-others", response_model=LogoutOthersResponse, status_code=status.HTTP_201_CREATED)
async def logout_others(request: Request, db: DbSession, user: CurrentUser) -> LogoutOthersResponse:
    session_id = _current_session_id(request)
    result = await auth_service.logout_others(db, user.id, session_id, _ctx(request))
    return LogoutOthersResponse(revoked=result["revoked"])


@router.get("/sessions")
async def sessions(request: Request, db: DbSession, user: CurrentUser) -> list[dict]:
    return await auth_service.list_sessions(db, user.id, _current_session_id(request))


@router.get("/me")
async def me(db: DbSession, user: CurrentUser) -> dict:
    profile = await auth_service.get_profile_summary(db, user.id)
    return {
        "id": user.id,
        "type": user.type,
        "roles": user.roles,
        "permissions": user.permissions,
        "client_id": user.client_id,
        "region_id": user.region_id,
        "office_id": user.office_id,
        "name": profile["name"],
        "email": profile["email"],
    }


@router.post("/password/reset-request", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def reset_request(dto: RequestPasswordResetRequest, request: Request, db: DbSession) -> OkResponse:
    await auth_service.request_password_reset(db, dto.identifier, _ctx(request))
    return OkResponse()


@router.post("/password/reset", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def reset_password(dto: ResetPasswordRequest, request: Request, db: DbSession) -> OkResponse:
    await auth_service.reset_password(db, dto.token, dto.new_password, _ctx(request))
    return OkResponse()


@router.post("/password/change", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def change_password(
    dto: ChangePasswordRequest, request: Request, db: DbSession, user: CurrentUser
) -> OkResponse:
    await auth_service.change_password(db, user.id, dto, _current_session_id(request), _ctx(request))
    return OkResponse()


@router.post("/verify-email", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def verify_email(dto: VerifyContactRequest, request: Request, db: DbSession) -> OkResponse:
    await auth_service.verify_email(db, dto.token, _ctx(request))
    return OkResponse()


@router.post("/verify-phone", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def verify_phone(dto: VerifyContactRequest, request: Request, db: DbSession, user: CurrentUser) -> OkResponse:
    await auth_service.verify_phone(db, dto.token, _ctx(request))
    return OkResponse()
