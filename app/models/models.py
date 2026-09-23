"""SQLAlchemy 2.0 deklarativ modellar.

MANBA: E:\\pgdata-shahpremium\\schema.sql — asl Prisma-boshqaruvidagi PostgreSQL
bazasining `pg_dump --schema-only` natijasi (haqiqiy, ishlab turgan dev baza,
prod'dan oldin qolgan nusxa). Bu fayl endi o'sha haqiqiy sxemaga ANIQ mos:

- Har bir `__tablename__` schema.sql'dagi haqiqiy jadval nomi bilan bir xil.
- Python-tomon atribut nomlari idiomatik snake_case, lekin har bir ustun uchun
  `mapped_column(...)` ning birinchi positional argumenti sifatida HAQIQIY
  camelCase (yoki boshqa) ustun nomi ko'rsatilgan (agar snake_case bilan mos
  kelmasa).
- Enum ustunlar haqiqiy Postgres native ENUM turlariga (`CREATE TYPE public."X"`)
  bog'langan (`postgresql.ENUM(..., create_type=False)`) — shunda yozish
  (INSERT/UPDATE) paytida ham to'g'ri ishlaydi, faqat o'qishda emas.
- Barcha timestamp ustunlar `timestamp(3) without time zone` (timezone YO'Q).
- Prisma `DateTime` maydonlari (hatto faqat sana ma'nosidagilar ham, masalan
  birthDate/hireDate/startDate) haqiqiy bazada `timestamp` — shu sababli bu
  yerda ham hammasi `DateTime()` (Date EMAS).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, ENUM as PG_ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDPKMixin
from app.models.enums import (
    AppointmentStatus,
    CasePriority,
    CaseStatus,
    ChatType,
    ClientType,
    ContractStatus,
    DocumentAccess,
    EmployeeKind,
    EmployeeStatus,
    IntegrationType,
    InvoiceStatus,
    NotificationChannel,
    PartnerStatus,
    PaymentCategory,
    PaymentDirection,
    PaymentMethod,
    PaymentStatus,
    QueueStatus,
    ServiceCategory,
    TaskPriority,
    TaskStatus,
    TimelineEventType,
    TimeOffType,
    UserType,
    VerificationTokenType,
)


def _enum(py_enum, name: str | None = None) -> PG_ENUM:
    """Haqiqiy Postgres native ENUM turiga (`CREATE TYPE public."<name>"`) bog'lash.

    `create_type=False` — bu enum turlari bazada ALLAQACHON mavjud (Prisma
    tomonidan yaratilgan), SQLAlchemy ularni qayta yaratishga urinmasligi kerak.
    """

    return PG_ENUM(py_enum, name=name or py_enum.__name__, create_type=False)


# ======================================================================
# IDENTITY / AUTH / RBAC
# ======================================================================


class User(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `users`."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column("passwordHash", String(255))
    type: Mapped[UserType] = mapped_column(_enum(UserType), default=UserType.CLIENT)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True)
    locale: Mapped[str] = mapped_column(String(10), default="uz")
    last_login_at: Mapped[Optional[datetime]] = mapped_column("lastLoginAt", DateTime(), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column("emailVerifiedAt", DateTime(), nullable=True)
    phone_verified_at: Mapped[Optional[datetime]] = mapped_column("phoneVerifiedAt", DateTime(), nullable=True)
    failed_login_count: Mapped[int] = mapped_column("failedLoginCount", Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column("lockedUntil", DateTime(), nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column("twoFactorEnabled", Boolean, default=False)
    two_factor_secret: Mapped[Optional[str]] = mapped_column("twoFactorSecret", String(255), nullable=True)
    region_id: Mapped[Optional[str]] = mapped_column("regionId", ForeignKey("regions.id"), nullable=True)
    office_id: Mapped[Optional[str]] = mapped_column("officeId", ForeignKey("offices.id"), nullable=True)

    region: Mapped[Optional["Region"]] = relationship(back_populates="users")
    office: Mapped[Optional["Office"]] = relationship(back_populates="users")
    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    preference: Mapped[Optional["UserPreference"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    client: Mapped[Optional["Client"]] = relationship(back_populates="user", uselist=False)
    employee: Mapped[Optional["Employee"]] = relationship(back_populates="user", uselist=False)
    lawyer: Mapped[Optional["Lawyer"]] = relationship(back_populates="user", uselist=False)
    advocate: Mapped[Optional["Advocate"]] = relationship(back_populates="user", uselist=False)
    roles: Mapped[list["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    schedules: Mapped[list["Schedule"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserProfile(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `profiles` (bizning eski nomlanish `user_profiles` edi)."""

    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), unique=True)
    first_name: Mapped[str] = mapped_column("firstName", String(100))
    last_name: Mapped[str] = mapped_column("lastName", String(100))
    middle_name: Mapped[Optional[str]] = mapped_column("middleName", String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column("avatarUrl", String(500), nullable=True)
    birth_date: Mapped[Optional[datetime]] = mapped_column("birthDate", DateTime(), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")


class UserPreference(UUIDPKMixin, Base):
    """Haqiqiy jadval: `user_preferences`. DIQQAT: bu jadvalda `createdAt` ustuni
    YO'Q — faqat `updatedAt` bor, shu sababli TimestampMixin ishlatilmaydi."""

    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), unique=True)
    locale: Mapped[str] = mapped_column(String(10), default="uz")
    theme: Mapped[str] = mapped_column(String(20), default="system")
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Tashkent")
    date_format: Mapped[str] = mapped_column("dateFormat", String(20), default="dd.MM.yyyy")
    notify_in_app: Mapped[bool] = mapped_column("notifyInApp", Boolean, default=True)
    notify_email: Mapped[bool] = mapped_column("notifyEmail", Boolean, default=True)
    notify_sms: Mapped[bool] = mapped_column("notifySms", Boolean, default=False)
    notify_push: Mapped[bool] = mapped_column("notifyPush", Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", DateTime(), default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="preference")


class Role(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `roles`. `isSystem` DB default'i `true` (bizda avval `false` edi).

    DIQQAT: `key` ustuni asl bazada native Postgres ENUM (`RoleKey`) edi, lekin
    SUPER_ADMIN UI orqali erkin yangi rol yarata olishi uchun oddiy `text`ga
    o'tkazildi (migratsiya: scripts/_migrate_roles_key.py). 7 ta tizim roli
    (`is_system=True`) hamon `RoleKey` qiymatlaridan foydalanadi — bu shunchaki
    ularning odatiy qiymati, endi DB darajasida majburiy emas."""

    __tablename__ = "roles"

    key: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column("isSystem", Boolean, default=True)

    users: Mapped[list["UserRole"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    permissions: Mapped[list["RolePermission"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class Permission(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `permissions`. DIQQAT: `updatedAt` ustuni YO'Q."""

    __tablename__ = "permissions"

    key: Mapped[str] = mapped_column(String(100), unique=True)
    resource: Mapped[str] = mapped_column(String(100), index=True)
    action: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    roles: Mapped[list["RolePermission"]] = relationship(back_populates="permission", cascade="all, delete-orphan")


class UserRole(Base):
    """Haqiqiy jadval: `user_roles` — composite PK (userId, roleId) + `assignedAt`."""

    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[str] = mapped_column("roleId", ForeignKey("roles.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column("assignedAt", DateTime(), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="roles")
    role: Mapped["Role"] = relationship(back_populates="users")


class RolePermission(Base):
    """Haqiqiy jadval: `role_permissions` — composite PK (roleId, permissionId), timestamp yo'q."""

    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column("roleId", ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[str] = mapped_column("permissionId", ForeignKey("permissions.id"), primary_key=True)

    role: Mapped["Role"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="roles")


class RefreshToken(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `refresh_tokens`. `lastUsedAt` NOT NULL DEFAULT now()."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column("tokenHash", String(255))
    family_id: Mapped[str] = mapped_column("familyId", String(64), index=True)
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column("userAgent", String(500), nullable=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime())
    revoked_at: Mapped[Optional[datetime]] = mapped_column("revokedAt", DateTime(), nullable=True)
    replaced_by_hash: Mapped[Optional[str]] = mapped_column("replacedByHash", String(255), nullable=True)
    last_used_at: Mapped[datetime] = mapped_column(
        "lastUsedAt", DateTime(), default=func.now(), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


class LoginAttempt(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `login_attempts`."""

    __tablename__ = "login_attempts"

    identifier: Mapped[str] = mapped_column(String(255), index=True)
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column("userAgent", String(500), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean)


class VerificationToken(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `verification_tokens`."""

    __tablename__ = "verification_tokens"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), index=True)
    type: Mapped[VerificationTokenType] = mapped_column(_enum(VerificationTokenType))
    token_hash: Mapped[str] = mapped_column("tokenHash", String(255))
    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime())
    consumed_at: Mapped[Optional[datetime]] = mapped_column("consumedAt", DateTime(), nullable=True)


# ======================================================================
# GEOGRAPHY / ORG STRUCTURE
# ======================================================================


class Region(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `regions`."""

    __tablename__ = "regions"

    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(150))

    offices: Mapped[list["Office"]] = relationship(back_populates="region")
    clients: Mapped[list["Client"]] = relationship(back_populates="region")
    users: Mapped[list["User"]] = relationship(back_populates="region")


class Office(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `offices`."""

    __tablename__ = "offices"

    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    region_id: Mapped[str] = mapped_column("regionId", ForeignKey("regions.id"))

    region: Mapped["Region"] = relationship(back_populates="offices")
    users: Mapped[list["User"]] = relationship(back_populates="office")
    cases: Mapped[list["Case"]] = relationship(back_populates="office")


# ======================================================================
# STAFF (Employee / Lawyer / Advocate) + Schedule/TimeOff
# ======================================================================


class Employee(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `employees`. `commissionPercent` DEFAULT 10 (bizda avval 0 edi)."""

    __tablename__ = "employees"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), unique=True)
    office_id: Mapped[Optional[str]] = mapped_column("officeId", ForeignKey("offices.id"), nullable=True)
    kind: Mapped[EmployeeKind] = mapped_column(_enum(EmployeeKind), default=EmployeeKind.STAFF)
    status: Mapped[EmployeeStatus] = mapped_column(_enum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    position: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience_years: Mapped[Optional[int]] = mapped_column("experienceYears", Integer, nullable=True)
    commission_percent: Mapped[Decimal] = mapped_column("commissionPercent", Numeric(5, 2), default=Decimal("10"))
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    hire_date: Mapped[Optional[datetime]] = mapped_column("hireDate", DateTime(), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="employee")
    clients: Mapped[list["Client"]] = relationship(back_populates="responsible_employee")
    cases: Mapped[list["Case"]] = relationship(back_populates="responsible_employee")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="responsible_employee")
    payouts: Mapped[list["Payout"]] = relationship(back_populates="employee")


class Lawyer(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `lawyers` — Employee'dan ALOHIDA, kichik professional reyestr
    (Case.lawyerId shu jadvalga ishora qiladi, Employee.id ga emas)."""

    __tablename__ = "lawyers"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), unique=True)
    specialization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    license_number: Mapped[Optional[str]] = mapped_column("licenseNumber", String(100), unique=True, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="lawyer")
    cases: Mapped[list["Case"]] = relationship(back_populates="lawyer")


class Advocate(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `advocates`. DIQQAT: `specialization`/`licenseNumber` maydonlari
    YO'Q (bu bizning eski taxminimiz edi) — haqiqiy ustun faqat `barNumber` (unique)."""

    __tablename__ = "advocates"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), unique=True)
    bar_number: Mapped[Optional[str]] = mapped_column("barNumber", String(100), unique=True, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="advocate")
    cases: Mapped[list["Case"]] = relationship(back_populates="advocate")


class Schedule(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `schedules`. Unique(userId, dayOfWeek)."""

    __tablename__ = "schedules"
    __table_args__ = (UniqueConstraint("userId", "dayOfWeek", name="schedules_userId_dayOfWeek_key"),)

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), index=True)
    day_of_week: Mapped[int] = mapped_column("dayOfWeek", Integer)
    start_time: Mapped[str] = mapped_column("startTime", String(5))  # "HH:MM"
    end_time: Mapped[str] = mapped_column("endTime", String(5))
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="schedules")


class TimeOff(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `time_off` (bizning eski nomlanish `time_offs` edi).
    `type` ustuni (TimeOffType, default VACATION) — bizda avval umuman yo'q edi."""

    __tablename__ = "time_off"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), index=True)
    type: Mapped[TimeOffType] = mapped_column(_enum(TimeOffType), default=TimeOffType.VACATION)
    start_at: Mapped[datetime] = mapped_column("startAt", DateTime())
    end_at: Mapped[datetime] = mapped_column("endAt", DateTime())
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship()


# ======================================================================
# CLIENTS / TIMELINE
# ======================================================================


class Client(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `clients`."""

    __tablename__ = "clients"

    user_id: Mapped[Optional[str]] = mapped_column("userId", ForeignKey("users.id"), unique=True, nullable=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    full_name: Mapped[str] = mapped_column("fullName", String(255))
    client_type: Mapped[ClientType] = mapped_column("clientType", _enum(ClientType), default=ClientType.INDIVIDUAL)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column("taxId", String(50), nullable=True)
    region_id: Mapped[Optional[str]] = mapped_column("regionId", ForeignKey("regions.id"), nullable=True)
    responsible_employee_id: Mapped[Optional[str]] = mapped_column(
        "responsibleEmployeeId", ForeignKey("employees.id"), nullable=True
    )
    first_contact_at: Mapped[Optional[datetime]] = mapped_column("firstContactAt", DateTime(), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    user: Mapped[Optional["User"]] = relationship(back_populates="client")
    region: Mapped[Optional["Region"]] = relationship(back_populates="clients")
    responsible_employee: Mapped[Optional["Employee"]] = relationship(back_populates="clients")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    cases: Mapped[list["Case"]] = relationship(back_populates="client")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="client")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="client")
    payments: Mapped[list["Payment"]] = relationship(back_populates="client")
    documents: Mapped[list["Document"]] = relationship(back_populates="client")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="client")
    tasks: Mapped[list["Task"]] = relationship(back_populates="client")
    queue_entries: Mapped[list["QueueEntry"]] = relationship(back_populates="client")
    chats: Mapped[list["Chat"]] = relationship(back_populates="client")


class TimelineEvent(UUIDPKMixin, Base):
    """Haqiqiy jadval: `timeline_events`. `createdAt`/`updatedAt` yo'q — faqat `occurredAt`."""

    __tablename__ = "timeline_events"

    client_id: Mapped[str] = mapped_column("clientId", ForeignKey("clients.id"), index=True)
    type: Mapped[TimelineEventType] = mapped_column(_enum(TimelineEventType))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actor_id: Mapped[Optional[str]] = mapped_column("actorId", ForeignKey("users.id"), nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column("occurredAt", DateTime(), server_default=func.now())

    client: Mapped["Client"] = relationship(back_populates="timeline_events")


# ======================================================================
# SERVICES CATALOG
# ======================================================================


class Service(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `services`."""

    __tablename__ = "services"

    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[ServiceCategory] = mapped_column(_enum(ServiceCategory), default=ServiceCategory.LEGAL)
    base_price: Mapped[Optional[Decimal]] = mapped_column("basePrice", Numeric(14, 2), nullable=True)
    sort_order: Mapped[int] = mapped_column("sortOrder", Integer, default=0)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True)

    case_links: Mapped[list["CaseService"]] = relationship(back_populates="service")


# ======================================================================
# CASES
# ======================================================================


class Case(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `cases`."""

    __tablename__ = "cases"

    number: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    case_type: Mapped[Optional[str]] = mapped_column("caseType", String(100), nullable=True)
    category: Mapped[Optional[ServiceCategory]] = mapped_column(_enum(ServiceCategory), nullable=True)
    priority: Mapped[CasePriority] = mapped_column(_enum(CasePriority), default=CasePriority.NORMAL)
    status: Mapped[CaseStatus] = mapped_column(_enum(CaseStatus), default=CaseStatus.NEW)
    opened_at: Mapped[Optional[datetime]] = mapped_column("openedAt", DateTime(), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column("closedAt", DateTime(), nullable=True)
    client_id: Mapped[str] = mapped_column("clientId", ForeignKey("clients.id"), index=True)
    responsible_employee_id: Mapped[Optional[str]] = mapped_column(
        "responsibleEmployeeId", ForeignKey("employees.id"), nullable=True
    )
    lawyer_id: Mapped[Optional[str]] = mapped_column("lawyerId", ForeignKey("lawyers.id"), nullable=True)
    advocate_id: Mapped[Optional[str]] = mapped_column("advocateId", ForeignKey("advocates.id"), nullable=True)
    office_id: Mapped[Optional[str]] = mapped_column("officeId", ForeignKey("offices.id"), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="cases")
    responsible_employee: Mapped[Optional["Employee"]] = relationship(back_populates="cases")
    lawyer: Mapped[Optional["Lawyer"]] = relationship(back_populates="cases")
    advocate: Mapped[Optional["Advocate"]] = relationship(back_populates="cases")
    office: Mapped[Optional["Office"]] = relationship(back_populates="cases")
    notes: Mapped[list["CaseNote"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    services: Mapped[list["CaseService"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="case")
    documents: Mapped[list["Document"]] = relationship(back_populates="case")
    tasks: Mapped[list["Task"]] = relationship(back_populates="case")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="case")
    payments: Mapped[list["Payment"]] = relationship(back_populates="case")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="case")
    chats: Mapped[list["Chat"]] = relationship(back_populates="case")


class CaseNote(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `case_notes`."""

    __tablename__ = "case_notes"

    case_id: Mapped[str] = mapped_column("caseId", ForeignKey("cases.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[Optional[str]] = mapped_column("authorId", ForeignKey("users.id"), nullable=True)

    case: Mapped["Case"] = relationship(back_populates="notes")


class CaseService(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `case_services`. DIQQAT: o'zining `id` PK'siga ega (composite
    PK EMAS) — (caseId, serviceId) ustida faqat UNIQUE INDEX bor."""

    __tablename__ = "case_services"
    __table_args__ = (
        UniqueConstraint("caseId", "serviceId", name="case_services_caseId_serviceId_key"),
    )

    case_id: Mapped[str] = mapped_column("caseId", ForeignKey("cases.id"), index=True)
    service_id: Mapped[str] = mapped_column("serviceId", ForeignKey("services.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Decimal] = mapped_column("unitPrice", Numeric(14, 2))

    case: Mapped["Case"] = relationship(back_populates="services")
    service: Mapped["Service"] = relationship(back_populates="case_links")


# ======================================================================
# CONTRACTS
# ======================================================================


class Contract(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `contracts`."""

    __tablename__ = "contracts"

    number: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[ContractStatus] = mapped_column(_enum(ContractStatus), default=ContractStatus.DRAFT)
    client_id: Mapped[str] = mapped_column("clientId", ForeignKey("clients.id"), index=True)
    case_id: Mapped[Optional[str]] = mapped_column("caseId", ForeignKey("cases.id"), nullable=True)
    responsible_employee_id: Mapped[Optional[str]] = mapped_column(
        "responsibleEmployeeId", ForeignKey("employees.id"), nullable=True
    )
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    commission_percent: Mapped[Optional[Decimal]] = mapped_column("commissionPercent", Numeric(5, 2), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column("startDate", DateTime(), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column("endDate", DateTime(), nullable=True)
    file_storage_key: Mapped[Optional[str]] = mapped_column("fileStorageKey", String(500), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column("fileName", String(255), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="contracts")
    case: Mapped[Optional["Case"]] = relationship(back_populates="contracts")
    responsible_employee: Mapped[Optional["Employee"]] = relationship(back_populates="contracts")
    documents: Mapped[list["Document"]] = relationship(back_populates="contract")
    payments: Mapped[list["Payment"]] = relationship(back_populates="contract")


# ======================================================================
# DOCUMENTS
# ======================================================================


class Document(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `documents`."""

    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[Optional[str]] = mapped_column("docType", String(100), nullable=True)
    case_id: Mapped[Optional[str]] = mapped_column("caseId", ForeignKey("cases.id"), nullable=True)
    contract_id: Mapped[Optional[str]] = mapped_column("contractId", ForeignKey("contracts.id"), nullable=True)
    client_id: Mapped[Optional[str]] = mapped_column("clientId", ForeignKey("clients.id"), nullable=True)
    access_level: Mapped[DocumentAccess] = mapped_column("accessLevel", _enum(DocumentAccess), default=DocumentAccess.OFFICE)
    storage_key: Mapped[str] = mapped_column("storageKey", String(500))
    mime_type: Mapped[Optional[str]] = mapped_column("mimeType", String(150), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column("sizeBytes", Integer, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    current_version: Mapped[int] = mapped_column("currentVersion", Integer, default=1)
    uploaded_by_id: Mapped[Optional[str]] = mapped_column("uploadedById", ForeignKey("users.id"), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    case: Mapped[Optional["Case"]] = relationship(back_populates="documents")
    contract: Mapped[Optional["Contract"]] = relationship(back_populates="documents")
    client: Mapped[Optional["Client"]] = relationship(back_populates="documents")
    versions: Mapped[list["DocumentVersion"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `document_versions`."""

    __tablename__ = "document_versions"
    __table_args__ = (UniqueConstraint("documentId", "version", name="document_versions_documentId_version_key"),)

    document_id: Mapped[str] = mapped_column("documentId", ForeignKey("documents.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column("storageKey", String(500))
    mime_type: Mapped[Optional[str]] = mapped_column("mimeType", String(150), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column("sizeBytes", Integer, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    uploaded_by_id: Mapped[Optional[str]] = mapped_column("uploadedById", ForeignKey("users.id"), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="versions")


# ======================================================================
# APPOINTMENTS / QUEUE
# ======================================================================


class Appointment(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `appointments`."""

    __tablename__ = "appointments"

    title: Mapped[str] = mapped_column(String(255))
    start_at: Mapped[datetime] = mapped_column("startAt", DateTime())
    end_at: Mapped[datetime] = mapped_column("endAt", DateTime())
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[AppointmentStatus] = mapped_column(_enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    assignee_id: Mapped[Optional[str]] = mapped_column("assigneeId", ForeignKey("users.id"), nullable=True)
    client_id: Mapped[Optional[str]] = mapped_column("clientId", ForeignKey("clients.id"), nullable=True)
    case_id: Mapped[Optional[str]] = mapped_column("caseId", ForeignKey("cases.id"), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    client: Mapped[Optional["Client"]] = relationship(back_populates="appointments")
    case: Mapped[Optional["Case"]] = relationship(back_populates="appointments")
    queue_entry: Mapped[Optional["QueueEntry"]] = relationship(back_populates="appointment", uselist=False)


class QueueEntry(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `queue_entries`. `date` ustuni ham `timestamp` (Date EMAS)."""

    __tablename__ = "queue_entries"

    date: Mapped[datetime] = mapped_column(DateTime(), index=True)
    number: Mapped[int] = mapped_column(Integer)
    status: Mapped[QueueStatus] = mapped_column(_enum(QueueStatus), default=QueueStatus.WAITING)
    assignee_id: Mapped[Optional[str]] = mapped_column("assigneeId", ForeignKey("users.id"), nullable=True)
    client_id: Mapped[Optional[str]] = mapped_column("clientId", ForeignKey("clients.id"), nullable=True)
    office_id: Mapped[Optional[str]] = mapped_column("officeId", ForeignKey("offices.id"), nullable=True)
    appointment_id: Mapped[Optional[str]] = mapped_column(
        "appointmentId", ForeignKey("appointments.id"), unique=True, nullable=True
    )
    joined_at: Mapped[datetime] = mapped_column("joinedAt", DateTime(), server_default=func.now())
    called_at: Mapped[Optional[datetime]] = mapped_column("calledAt", DateTime(), nullable=True)

    client: Mapped[Optional["Client"]] = relationship(back_populates="queue_entries")
    appointment: Mapped[Optional["Appointment"]] = relationship(back_populates="queue_entry")


# ======================================================================
# TASKS (KANBAN)
# ======================================================================


class Task(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `tasks`."""

    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[Optional[str]] = mapped_column("assigneeId", ForeignKey("users.id"), nullable=True)
    author_id: Mapped[Optional[str]] = mapped_column("authorId", ForeignKey("users.id"), nullable=True)
    case_id: Mapped[Optional[str]] = mapped_column("caseId", ForeignKey("cases.id"), nullable=True)
    client_id: Mapped[Optional[str]] = mapped_column("clientId", ForeignKey("clients.id"), nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column("dueDate", DateTime(), nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(_enum(TaskPriority), default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(_enum(TaskStatus), default=TaskStatus.TODO)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    case: Mapped[Optional["Case"]] = relationship(back_populates="tasks")
    client: Mapped[Optional["Client"]] = relationship(back_populates="tasks")


# ======================================================================
# PAYMENTS / INVOICES / PAYOUTS
# ======================================================================


class Payment(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `payments`."""

    __tablename__ = "payments"

    client_id: Mapped[str] = mapped_column("clientId", ForeignKey("clients.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    direction: Mapped[PaymentDirection] = mapped_column(_enum(PaymentDirection), default=PaymentDirection.INCOME)
    category: Mapped[PaymentCategory] = mapped_column(_enum(PaymentCategory), default=PaymentCategory.SERVICES)
    method: Mapped[Optional[PaymentMethod]] = mapped_column(_enum(PaymentMethod), nullable=True)
    case_id: Mapped[Optional[str]] = mapped_column("caseId", ForeignKey("cases.id"), nullable=True)
    contract_id: Mapped[Optional[str]] = mapped_column("contractId", ForeignKey("contracts.id"), nullable=True)
    invoice_id: Mapped[Optional[str]] = mapped_column("invoiceId", ForeignKey("invoices.id"), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(_enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider_ref: Mapped[Optional[str]] = mapped_column("providerRef", String(255), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column("paidAt", DateTime(), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="payments")
    case: Mapped[Optional["Case"]] = relationship(back_populates="payments")
    contract: Mapped[Optional["Contract"]] = relationship(back_populates="payments")
    invoice: Mapped[Optional["Invoice"]] = relationship(back_populates="payments")


class Invoice(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `invoices`."""

    __tablename__ = "invoices"

    number: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[InvoiceStatus] = mapped_column(_enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    client_id: Mapped[str] = mapped_column("clientId", ForeignKey("clients.id"), index=True)
    case_id: Mapped[Optional[str]] = mapped_column("caseId", ForeignKey("cases.id"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    due_date: Mapped[Optional[datetime]] = mapped_column("dueDate", DateTime(), nullable=True)
    issued_at: Mapped[Optional[datetime]] = mapped_column("issuedAt", DateTime(), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    client: Mapped["Client"] = relationship(back_populates="invoices")
    case: Mapped[Optional["Case"]] = relationship(back_populates="invoices")
    payments: Mapped[list["Payment"]] = relationship(back_populates="invoice")


class Payout(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `payouts` (xodim komissiya to'lovlari). Bizda avval BUTUNLAY
    yo'q edi — hech qanday modul/router hali ulanmagan (dist/**/*.js ichida
    `prisma.payout` chaqiruvi topilmadi, demak asl loyihada ham controller
    bo'lmagan yoki ochilmagan bo'lishi mumkin — hozircha faqat model qo'shildi)."""

    __tablename__ = "payouts"

    employee_id: Mapped[str] = mapped_column("employeeId", ForeignKey("employees.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    status: Mapped[PaymentStatus] = mapped_column(_enum(PaymentStatus), default=PaymentStatus.PENDING)
    period_from: Mapped[Optional[datetime]] = mapped_column("periodFrom", DateTime(), nullable=True)
    period_to: Mapped[Optional[datetime]] = mapped_column("periodTo", DateTime(), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column("paidAt", DateTime(), nullable=True)

    employee: Mapped["Employee"] = relationship(back_populates="payouts")


# ======================================================================
# NOTIFICATIONS
# ======================================================================


class Notification(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `notifications`. DIQQAT: `updatedAt` ustuni YO'Q."""

    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), index=True)
    event: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    channel: Mapped[NotificationChannel] = mapped_column(_enum(NotificationChannel), default=NotificationChannel.IN_APP)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column("isRead", Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column("readAt", DateTime(), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column("sentAt", DateTime(), nullable=True)

    user: Mapped["User"] = relationship()


# ======================================================================
# CHAT
# ======================================================================


class Chat(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `chats`."""

    __tablename__ = "chats"

    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[ChatType] = mapped_column(_enum(ChatType), default=ChatType.DIRECT)
    is_internal: Mapped[bool] = mapped_column("isInternal", Boolean, default=False)
    case_id: Mapped[Optional[str]] = mapped_column("caseId", ForeignKey("cases.id"), nullable=True)
    client_id: Mapped[Optional[str]] = mapped_column("clientId", ForeignKey("clients.id"), nullable=True)

    case: Mapped[Optional["Case"]] = relationship(back_populates="chats")
    client: Mapped[Optional["Client"]] = relationship(back_populates="chats")
    members: Mapped[list["ChatMember"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")


class ChatMember(UUIDPKMixin, Base):
    """Haqiqiy jadval: `chat_members`. Unique(chatId, userId)."""

    __tablename__ = "chat_members"
    __table_args__ = (UniqueConstraint("chatId", "userId", name="chat_members_chatId_userId_key"),)

    chat_id: Mapped[str] = mapped_column("chatId", ForeignKey("chats.id"), index=True)
    user_id: Mapped[str] = mapped_column("userId", ForeignKey("users.id"), index=True)
    joined_at: Mapped[datetime] = mapped_column("joinedAt", DateTime(), server_default=func.now())
    last_read_at: Mapped[Optional[datetime]] = mapped_column("lastReadAt", DateTime(), nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()


class Message(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `messages`."""

    __tablename__ = "messages"

    chat_id: Mapped[str] = mapped_column("chatId", ForeignKey("chats.id"), index=True)
    sender_id: Mapped[str] = mapped_column("senderId", ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    attachment_storage_key: Mapped[Optional[str]] = mapped_column("attachmentStorageKey", String(500), nullable=True)
    attachment_name: Mapped[Optional[str]] = mapped_column("attachmentName", String(255), nullable=True)
    attachment_mime: Mapped[Optional[str]] = mapped_column("attachmentMime", String(150), nullable=True)
    edited_at: Mapped[Optional[datetime]] = mapped_column("editedAt", DateTime(), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime(), nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship()


# ======================================================================
# AUDIT
# ======================================================================


class AuditLog(UUIDPKMixin, CreatedAtMixin, Base):
    """Haqiqiy jadval: `audit_logs`."""

    __tablename__ = "audit_logs"

    actor_id: Mapped[Optional[str]] = mapped_column("actorId", ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(255), index=True)
    entity: Mapped[str] = mapped_column(String(100), index=True)
    entity_id: Mapped[Optional[str]] = mapped_column("entityId", String(64), nullable=True)
    before: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column("userAgent", String(500), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column("requestId", String(100), nullable=True)


# ======================================================================
# INTEGRATIONS
# ======================================================================


class Integration(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `integrations`."""

    __tablename__ = "integrations"

    key: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[Optional[IntegrationType]] = mapped_column(_enum(IntegrationType), nullable=True)
    is_enabled: Mapped[bool] = mapped_column("isEnabled", Boolean, default=False)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class PartnerOrganization(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `partner_organizations`."""

    __tablename__ = "partner_organizations"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contacts: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    contract_number: Mapped[Optional[str]] = mapped_column("contractNumber", String(100), nullable=True)
    contract_ends_at: Mapped[Optional[datetime]] = mapped_column("contractEndsAt", DateTime(), nullable=True)
    services: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[PartnerStatus] = mapped_column(_enum(PartnerStatus), default=PartnerStatus.ACTIVE)
    logo_storage_key: Mapped[Optional[str]] = mapped_column("logoStorageKey", String(500), nullable=True)


# ======================================================================
# SETTINGS
# ======================================================================


class Setting(UUIDPKMixin, TimestampMixin, Base):
    """Haqiqiy jadval: `settings`."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(150), unique=True)
    value: Mapped[dict] = mapped_column(JSONB)
    scope: Mapped[str] = mapped_column(String(50), default="GLOBAL")
