import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDPKMixin:
    """Prisma `@default(uuid())` ekvivalenti — string UUID primary key (haqiqiy
    bazada `id text NOT NULL`, klient tomonda generatsiya qilinadi)."""

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    """Prisma `createdAt @default(now())` / `updatedAt @updatedAt` juftligi.

    Haqiqiy bazada (schema.sql) ikkalasi ham `timestamp(3) without time zone`:
    - "createdAt" ustunida DB darajasida `DEFAULT CURRENT_TIMESTAMP` bor ->
      `server_default=func.now()` ishlatiladi (baza o'zi to'ldiradi).
    - "updatedAt" ustuni NOT NULL, lekin DB darajasida DEFAULT YO'Q (Prisma buni
      ilova darajasida to'ldiradi) -> `server_default` EMAS, `default=func.now()`
      ishlatiladi (SQLAlchemy INSERT ichiga aniq ifoda sifatida qo'shadi).
    """

    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", DateTime(), default=func.now(), onupdate=func.now()
    )


class CreatedAtMixin:
    """Faqat `createdAt` ustuniga ega jadvallar uchun (haqiqiy bazada `updatedAt`
    ustuni bo'lmagan jadvallar: audit_logs, case_notes, case_services,
    document_versions, login_attempts, messages, payouts, permissions,
    queue_entries, refresh_tokens, verification_tokens)."""

    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(), server_default=func.now())
