import re

from pydantic import BaseModel, EmailStr, Field, field_validator

STRONG_PASSWORD = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


def _validate_strong(value: str) -> str:
    if not STRONG_PASSWORD.match(value):
        raise ValueError("Parol kamida 8 belgi, harf va raqamdan iborat boʻlsin")
    return value


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)
    first_name: str
    last_name: str

    _validate_password = field_validator("password")(_validate_strong)


class RegisterResponse(BaseModel):
    user_id: str


class LoginRequest(BaseModel):
    identifier: str
    password: str = Field(min_length=1)
    otp: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class RequestPasswordResetRequest(BaseModel):
    identifier: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

    _validate_password = field_validator("new_password")(_validate_strong)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

    _validate_password = field_validator("new_password")(_validate_strong)


class VerifyContactRequest(BaseModel):
    token: str


class OkResponse(BaseModel):
    ok: bool = True


class CsrfResponse(BaseModel):
    csrf_token: str


class SessionInfo(BaseModel):
    id: str
    ip: str | None
    user_agent: str | None
    label: str | None
    last_used_at: object
    created_at: object
    current: bool


class LogoutOthersResponse(BaseModel):
    revoked: int
