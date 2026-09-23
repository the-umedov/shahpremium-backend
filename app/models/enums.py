"""Enumlar.

MANBA: E:\\pgdata-shahpremium\\schema.sql — asl Prisma-boshqaruvidagi PostgreSQL
bazasining `pg_dump --schema-only` natijasi (haqiqiy, ishlab turgan dev baza).
Quyidagi barcha enum a'zolari shu fayldagi `CREATE TYPE public."<Name>" AS ENUM (...)`
bloklaridan SO'ZMA-SO'Z ko'chirilgan — taxmin EMAS, aniq ma'lumot.
Oldingi versiyada (kompilyatsiya qilingan JS'dan tiklangan) bir nechta a'zolar
noto'g'ri/yo'q edi — bu fayl ularning barchasini tuzatadi.
"""

from enum import Enum


class RoleKey(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    LAWYER = "LAWYER"
    ADVOCATE = "ADVOCATE"
    ACCOUNTANT = "ACCOUNTANT"
    MANAGER = "MANAGER"
    CLIENT = "CLIENT"


class UserType(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    LAWYER = "LAWYER"
    ADVOCATE = "ADVOCATE"
    CLIENT = "CLIENT"


class VerificationTokenType(str, Enum):
    EMAIL_VERIFY = "EMAIL_VERIFY"
    PHONE_VERIFY = "PHONE_VERIFY"
    PASSWORD_RESET = "PASSWORD_RESET"
    OTP = "OTP"


class CaseStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"
    NEW = "NEW"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CasePriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ServiceCategory(str, Enum):
    LEGAL = "LEGAL"
    ADVOCACY = "ADVOCACY"
    CRIMINAL = "CRIMINAL"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    CIVIL = "CIVIL"
    ECONOMIC = "ECONOMIC"
    INVESTIGATIVE = "INVESTIGATIVE"
    REQUEST = "REQUEST"
    APPEAL = "APPEAL"


class ContractStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    UNDER_REVIEW = "UNDER_REVIEW"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class PaymentCategory(str, Enum):
    SERVICES = "SERVICES"
    STATE_FEE = "STATE_FEE"
    POSTAL = "POSTAL"
    OTHER = "OTHER"


class ClientType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"


class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_VACATION = "ON_VACATION"
    BUSY = "BUSY"
    UNAVAILABLE = "UNAVAILABLE"


class PartnerStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class IntegrationType(str, Enum):
    PAYMENT = "PAYMENT"
    EMAIL = "EMAIL"
    SMS = "SMS"
    MAPS = "MAPS"
    CALENDAR = "CALENDAR"
    EXTERNAL_ORG = "EXTERNAL_ORG"
    ACCOUNTING = "ACCOUNTING"
    EDMS = "EDMS"


class TimelineEventType(str, Enum):
    CREATED = "CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    CASE_ADDED = "CASE_ADDED"
    CONTRACT_ADDED = "CONTRACT_ADDED"
    DOCUMENT_ADDED = "DOCUMENT_ADDED"
    PAYMENT_ADDED = "PAYMENT_ADDED"
    APPOINTMENT_ADDED = "APPOINTMENT_ADDED"
    TASK_ADDED = "TASK_ADDED"
    NOTE = "NOTE"
    CONTACT = "CONTACT"


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"


class EmployeeKind(str, Enum):
    LAWYER = "LAWYER"
    ADVOCATE = "ADVOCATE"
    STAFF = "STAFF"


class QueueStatus(str, Enum):
    WAITING = "WAITING"
    INVITED = "INVITED"
    IN_SERVICE = "IN_SERVICE"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class PaymentDirection(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    ONLINE = "ONLINE"


class DocumentAccess(str, Enum):
    PRIVATE = "PRIVATE"
    OFFICE = "OFFICE"
    CLIENT_SHARED = "CLIENT_SHARED"
    RESTRICTED = "RESTRICTED"


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    IN_APP = "IN_APP"


class ChatType(str, Enum):
    DIRECT = "DIRECT"
    GROUP = "GROUP"


class TimeOffType(str, Enum):
    VACATION = "VACATION"
    SICK = "SICK"
    OTHER = "OTHER"
