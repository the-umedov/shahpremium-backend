from __future__ import annotations

from datetime import datetime
from app.core.timeutils import utcnow

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import RoleKey, UserType, VerificationTokenType
from app.models.models import Role, RolePermission, User, UserProfile, UserRole
from app.modules.authentication.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
)
from app.modules.authentication.security_events import SecurityEvent
from app.modules.authentication.services import (
    brute_force_service as brute_force,
    otp_service,
    password_service as passwords,
    security_event_service as security,
    session_service as sessions,
    token_service as tokens,
    verification_service as verification,
)
from app.modules.authentication.services.token_service import RequestMeta


def _is_email(identifier: str) -> bool:
    return "@" in identifier


async def get_profile_summary(db: AsyncSession, user_id: str) -> dict:
    """`/auth/me` uchun ko'rsatiladigan ism/email — header'da xom "TYPE · id"
    o'rniga haqiqiy ism chiqarish uchun (profil bo'lmasa email'ga tushadi)."""
    user = (
        await db.execute(select(User).options(selectinload(User.profile)).where(User.id == user_id))
    ).scalar_one()
    if user.profile and (user.profile.first_name or user.profile.last_name):
        name = f"{user.profile.first_name or ''} {user.profile.last_name or ''}".strip()
    else:
        name = user.email
    return {"name": name, "email": user.email}


async def build_claims(db: AsyncSession, user_id: str) -> dict:
    """Access claim'larini bazadan yigʻish."""
    user = (
        await db.execute(
            select(User)
            .options(
                selectinload(User.client),
                selectinload(User.roles)
                .selectinload(UserRole.role)
                .selectinload(Role.permissions)
                .selectinload(RolePermission.permission),
            )
            .where(User.id == user_id)
        )
    ).scalar_one()

    roles = [ur.role.key for ur in user.roles]
    permissions = sorted({rp.permission.key for ur in user.roles for rp in ur.role.permissions})

    return {
        "sub": user.id,
        "type": user.type,
        "roles": roles,
        "permissions": permissions,
        "clientId": user.client.id if user.client else None,
        "regionId": user.region_id,
        "officeId": user.office_id,
    }


async def issue_tokens(db: AsyncSession, user_id: str, meta: RequestMeta) -> dict:
    claims = await build_claims(db, user_id)
    access_token = tokens.sign_access_token(claims)
    issued = await tokens.issue_refresh_session(db, user_id, meta)
    return {"access_token": access_token, "refresh_token": issued["token"], "session_id": issued["session_id"]}


# ============================================================
# REGISTRATION
# ============================================================
async def register(db: AsyncSession, dto: RegisterRequest) -> dict:
    condition = (User.email == dto.email) | (User.phone == dto.phone) if dto.phone else (User.email == dto.email)
    existing = (await db.execute(select(User.id).where(condition))).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bunday email yoki telefon allaqachon mavjud")

    password_hash = await passwords.hash(dto.password)

    client_role = (await db.execute(select(Role).where(Role.key == RoleKey.CLIENT))).scalar_one()

    user = User(email=dto.email, phone=dto.phone, password_hash=password_hash, type=UserType.CLIENT)
    db.add(user)
    await db.flush()
    db.add(UserProfile(user_id=user.id, first_name=dto.first_name, last_name=dto.last_name))
    db.add(UserRole(user_id=user.id, role_id=client_role.id))
    await db.commit()

    await verification.create_token(db, user.id, VerificationTokenType.EMAIL_VERIFY)
    return {"user_id": user.id}


# ============================================================
# LOGIN
# ============================================================
async def login(db: AsyncSession, dto: LoginRequest, meta: RequestMeta) -> dict:
    identifier, password, otp = dto.identifier, dto.password, dto.otp

    failures = await brute_force.recent_failures(db, identifier, meta.ip)
    if failures >= 10:
        await security.record(
            db,
            event=SecurityEvent.SUSPICIOUS_ACTIVITY,
            ctx=meta,
            meta={"identifier": identifier, "failures": failures},
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Juda koʻp urinishlar. Keyinroq urinib koʻring.")

    query = select(User).where(User.email == identifier) if _is_email(identifier) else select(User).where(User.phone == identifier)
    user = (await db.execute(query)).scalar_one_or_none()

    valid = (
        await passwords.verify(user.password_hash, password)
        if user
        else await passwords.verify(passwords.DUMMY_HASH, password)
    )

    async def fail_login(user_id: str | None) -> None:
        await brute_force.record_attempt(
            db, brute_force.AttemptParams(identifier=identifier, ip=meta.ip, user_agent=meta.user_agent, success=False)
        )
        if user_id:
            result = await brute_force.register_failure(db, user_id)
            await security.record(
                db,
                event=SecurityEvent.ACCOUNT_LOCKED if result["locked"] else SecurityEvent.LOGIN_FAILED,
                user_id=user_id,
                ctx=meta,
            )
        else:
            await security.record(db, event=SecurityEvent.LOGIN_FAILED, ctx=meta, meta={"identifier": identifier})

    if not user or not user.is_active or user.deleted_at:
        await fail_login(user.id if user else None)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Login yoki parol notoʻgʻri")

    if brute_force.is_locked(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Hisob vaqtincha bloklangan")

    if not valid:
        await fail_login(user.id)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Login yoki parol notoʻgʻri")

    if user.two_factor_enabled:
        if not otp:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "2FA kodi talab qilinadi")
        ok = otp_service.verify(otp, user.two_factor_secret) if user.two_factor_secret else False
        if not ok:
            await fail_login(user.id)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "2FA kodi notoʻgʻri")

    await brute_force.reset(db, user.id)
    await brute_force.record_attempt(
        db, brute_force.AttemptParams(identifier=identifier, ip=meta.ip, user_agent=meta.user_agent, success=True)
    )
    user.last_login_at = utcnow()
    await db.commit()

    await security.record(db, event=SecurityEvent.LOGIN, user_id=user.id, ctx=meta)
    return await issue_tokens(db, user.id, meta)


# ============================================================
# REFRESH / SESSIONS
# ============================================================
async def refresh(db: AsyncSession, presented_refresh_token: str, meta: RequestMeta) -> dict:
    rotated = await tokens.rotate_refresh_token(db, presented_refresh_token, meta)
    claims = await build_claims(db, rotated["user_id"])
    return {
        "access_token": tokens.sign_access_token(claims),
        "refresh_token": rotated["token"],
        "session_id": rotated["session_id"],
    }


async def logout(db: AsyncSession, session_id: str, user_id: str, ctx: RequestMeta) -> None:
    await tokens.revoke_session(db, session_id)
    await security.record(db, event=SecurityEvent.LOGOUT, user_id=user_id, ctx=ctx)


async def logout_others(db: AsyncSession, user_id: str, keep_session_id: str | None, ctx: RequestMeta) -> dict:
    count = await tokens.revoke_all_except(db, user_id, keep_session_id)
    await security.record(db, event=SecurityEvent.LOGOUT_ALL, user_id=user_id, ctx=ctx, meta={"revoked": count})
    return {"revoked": count}


async def list_sessions(db: AsyncSession, user_id: str, current_session_id: str | None) -> list[dict]:
    return await sessions.list_active(db, user_id, current_session_id)


# ============================================================
# PASSWORD
# ============================================================
async def request_password_reset(db: AsyncSession, identifier: str, ctx: RequestMeta) -> None:
    query = select(User.id).where(User.email == identifier) if _is_email(identifier) else select(User.id).where(User.phone == identifier)
    user_id = (await db.execute(query)).scalar_one_or_none()
    # mavjudlikni oshkor qilmaymiz — javob har doim bir xil
    if user_id:
        await verification.create_token(db, user_id, VerificationTokenType.PASSWORD_RESET)
        await security.record(db, event=SecurityEvent.PASSWORD_RESET_REQUEST, user_id=user_id, ctx=ctx)


async def reset_password(db: AsyncSession, token: str, new_password: str, ctx: RequestMeta) -> None:
    res = await verification.consume(db, VerificationTokenType.PASSWORD_RESET, token)
    if not res:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token yaroqsiz yoki muddati oʻtgan")
    user_id = res["user_id"]
    password_hash = await passwords.hash(new_password)
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    user.password_hash = password_hash
    await tokens.revoke_all_except(db, user_id, None)
    await db.commit()
    await security.record(db, event=SecurityEvent.PASSWORD_RESET, user_id=user_id, ctx=ctx)


async def change_password(
    db: AsyncSession,
    user_id: str,
    dto: ChangePasswordRequest,
    current_session_id: str | None,
    ctx: RequestMeta,
) -> None:
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    ok = await passwords.verify(user.password_hash, dto.current_password)
    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Joriy parol notoʻgʻri")
    user.password_hash = await passwords.hash(dto.new_password)
    await db.commit()
    await tokens.revoke_all_except(db, user_id, current_session_id)
    await security.record(db, event=SecurityEvent.PASSWORD_CHANGE, user_id=user_id, ctx=ctx)


# ============================================================
# KONTAKT TASDIQLASH
# ============================================================
async def verify_email(db: AsyncSession, token: str, ctx: RequestMeta) -> None:
    res = await verification.consume(db, VerificationTokenType.EMAIL_VERIFY, token)
    if not res:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token yaroqsiz yoki muddati oʻtgan")
    user = (await db.execute(select(User).where(User.id == res["user_id"]))).scalar_one()
    user.email_verified_at = utcnow()
    await db.commit()
    await security.record(db, event=SecurityEvent.CONTACT_VERIFIED, user_id=user.id, ctx=ctx, meta={"contact": "email"})


async def verify_phone(db: AsyncSession, token: str, ctx: RequestMeta) -> None:
    res = await verification.consume(db, VerificationTokenType.PHONE_VERIFY, token)
    if not res:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Kod yaroqsiz yoki muddati oʻtgan")
    user = (await db.execute(select(User).where(User.id == res["user_id"]))).scalar_one()
    user.phone_verified_at = utcnow()
    await db.commit()
    await security.record(db, event=SecurityEvent.CONTACT_VERIFIED, user_id=user.id, ctx=ctx, meta={"contact": "phone"})
