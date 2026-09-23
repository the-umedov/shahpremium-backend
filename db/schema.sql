--
-- PostgreSQL database dump
--


-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: AppointmentStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."AppointmentStatus" AS ENUM (
    'SCHEDULED',
    'COMPLETED',
    'CANCELLED',
    'NO_SHOW',
    'PENDING',
    'CONFIRMED',
    'IN_PROGRESS'
);


--
-- Name: CasePriority; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."CasePriority" AS ENUM (
    'LOW',
    'NORMAL',
    'HIGH',
    'URGENT'
);


--
-- Name: CaseStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."CaseStatus" AS ENUM (
    'DRAFT',
    'OPEN',
    'IN_PROGRESS',
    'ON_HOLD',
    'CLOSED',
    'ARCHIVED',
    'NEW',
    'WAITING',
    'COMPLETED',
    'CANCELLED'
);


--
-- Name: ChatType; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."ChatType" AS ENUM (
    'DIRECT',
    'GROUP'
);


--
-- Name: ClientType; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."ClientType" AS ENUM (
    'INDIVIDUAL',
    'ORGANIZATION'
);


--
-- Name: ContractStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."ContractStatus" AS ENUM (
    'DRAFT',
    'ACTIVE',
    'EXPIRED',
    'TERMINATED',
    'UNDER_REVIEW',
    'COMPLETED',
    'ARCHIVED'
);


--
-- Name: DocumentAccess; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."DocumentAccess" AS ENUM (
    'PRIVATE',
    'OFFICE',
    'CLIENT_SHARED',
    'RESTRICTED'
);


--
-- Name: EmployeeKind; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."EmployeeKind" AS ENUM (
    'LAWYER',
    'ADVOCATE',
    'STAFF'
);


--
-- Name: EmployeeStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."EmployeeStatus" AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'ON_VACATION',
    'BUSY',
    'UNAVAILABLE'
);


--
-- Name: IntegrationType; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."IntegrationType" AS ENUM (
    'PAYMENT',
    'EMAIL',
    'SMS',
    'MAPS',
    'CALENDAR',
    'EXTERNAL_ORG',
    'ACCOUNTING',
    'EDMS'
);


--
-- Name: InvoiceStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."InvoiceStatus" AS ENUM (
    'DRAFT',
    'ISSUED',
    'PAID',
    'OVERDUE',
    'CANCELLED'
);


--
-- Name: NotificationChannel; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."NotificationChannel" AS ENUM (
    'EMAIL',
    'SMS',
    'PUSH',
    'IN_APP'
);


--
-- Name: PartnerStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."PartnerStatus" AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);


--
-- Name: PaymentCategory; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."PaymentCategory" AS ENUM (
    'SERVICES',
    'STATE_FEE',
    'POSTAL',
    'OTHER'
);


--
-- Name: PaymentDirection; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."PaymentDirection" AS ENUM (
    'INCOME',
    'EXPENSE'
);


--
-- Name: PaymentMethod; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."PaymentMethod" AS ENUM (
    'CASH',
    'CARD',
    'BANK_TRANSFER',
    'ONLINE'
);


--
-- Name: PaymentStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."PaymentStatus" AS ENUM (
    'PENDING',
    'PAID',
    'PARTIAL',
    'REFUNDED',
    'FAILED',
    'CANCELLED'
);


--
-- Name: QueueStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."QueueStatus" AS ENUM (
    'WAITING',
    'INVITED',
    'IN_SERVICE',
    'DONE',
    'CANCELLED'
);


--
-- Name: RoleKey; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."RoleKey" AS ENUM (
    'SUPER_ADMIN',
    'ADMIN',
    'LAWYER',
    'ADVOCATE',
    'ACCOUNTANT',
    'MANAGER',
    'CLIENT'
);


--
-- Name: ServiceCategory; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."ServiceCategory" AS ENUM (
    'LEGAL',
    'ADVOCACY',
    'CRIMINAL',
    'ADMINISTRATIVE',
    'CIVIL',
    'ECONOMIC',
    'INVESTIGATIVE',
    'REQUEST',
    'APPEAL'
);


--
-- Name: TaskPriority; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."TaskPriority" AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'URGENT'
);


--
-- Name: TaskStatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."TaskStatus" AS ENUM (
    'TODO',
    'IN_PROGRESS',
    'DONE',
    'CANCELLED',
    'OVERDUE'
);


--
-- Name: TimeOffType; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."TimeOffType" AS ENUM (
    'VACATION',
    'SICK',
    'OTHER'
);


--
-- Name: TimelineEventType; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."TimelineEventType" AS ENUM (
    'CREATED',
    'STATUS_CHANGED',
    'CASE_ADDED',
    'CONTRACT_ADDED',
    'DOCUMENT_ADDED',
    'PAYMENT_ADDED',
    'APPOINTMENT_ADDED',
    'TASK_ADDED',
    'NOTE',
    'CONTACT'
);


--
-- Name: UserType; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."UserType" AS ENUM (
    'EMPLOYEE',
    'LAWYER',
    'ADVOCATE',
    'CLIENT'
);


--
-- Name: VerificationTokenType; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public."VerificationTokenType" AS ENUM (
    'EMAIL_VERIFY',
    'PHONE_VERIFY',
    'PASSWORD_RESET',
    'OTP'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: _prisma_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public._prisma_migrations (
    id character varying(36) NOT NULL,
    checksum character varying(64) NOT NULL,
    finished_at timestamp with time zone,
    migration_name character varying(255) NOT NULL,
    logs text,
    rolled_back_at timestamp with time zone,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    applied_steps_count integer DEFAULT 0 NOT NULL
);


--
-- Name: advocates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.advocates (
    id text NOT NULL,
    "userId" text NOT NULL,
    "barNumber" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone
);


--
-- Name: appointments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.appointments (
    id text NOT NULL,
    title text NOT NULL,
    "startAt" timestamp(3) without time zone NOT NULL,
    "endAt" timestamp(3) without time zone NOT NULL,
    location text,
    status public."AppointmentStatus" DEFAULT 'PENDING'::public."AppointmentStatus" NOT NULL,
    "caseId" text,
    "clientId" text,
    "assigneeId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id text NOT NULL,
    "actorId" text,
    action text NOT NULL,
    entity text NOT NULL,
    "entityId" text,
    before jsonb,
    after jsonb,
    ip text,
    "requestId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reason text,
    "userAgent" text
);


--
-- Name: case_notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.case_notes (
    id text NOT NULL,
    "caseId" text NOT NULL,
    "authorId" text,
    body text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: case_services; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.case_services (
    id text NOT NULL,
    "caseId" text NOT NULL,
    "serviceId" text NOT NULL,
    quantity integer DEFAULT 1 NOT NULL,
    "unitPrice" numeric(14,2) NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: cases; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cases (
    id text NOT NULL,
    number text NOT NULL,
    title text NOT NULL,
    description text,
    status public."CaseStatus" DEFAULT 'NEW'::public."CaseStatus" NOT NULL,
    "openedAt" timestamp(3) without time zone,
    "closedAt" timestamp(3) without time zone,
    "clientId" text NOT NULL,
    "lawyerId" text,
    "advocateId" text,
    "officeId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "caseType" text,
    category public."ServiceCategory",
    priority public."CasePriority" DEFAULT 'NORMAL'::public."CasePriority" NOT NULL,
    "responsibleEmployeeId" text
);


--
-- Name: chat_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_members (
    id text NOT NULL,
    "chatId" text NOT NULL,
    "userId" text NOT NULL,
    "joinedAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "lastReadAt" timestamp(3) without time zone
);


--
-- Name: chats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chats (
    id text NOT NULL,
    title text,
    "caseId" text,
    "clientId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "isInternal" boolean DEFAULT false NOT NULL,
    type public."ChatType" DEFAULT 'DIRECT'::public."ChatType" NOT NULL
);


--
-- Name: clients; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clients (
    id text NOT NULL,
    code text NOT NULL,
    "userId" text,
    "clientType" public."ClientType" DEFAULT 'INDIVIDUAL'::public."ClientType" NOT NULL,
    "fullName" text NOT NULL,
    "taxId" text,
    phone text,
    email text,
    address text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "firstContactAt" timestamp(3) without time zone,
    "regionId" text,
    "responsibleEmployeeId" text
);


--
-- Name: contracts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contracts (
    id text NOT NULL,
    number text NOT NULL,
    status public."ContractStatus" DEFAULT 'DRAFT'::public."ContractStatus" NOT NULL,
    amount numeric(14,2),
    currency text DEFAULT 'UZS'::text NOT NULL,
    "startDate" timestamp(3) without time zone,
    "endDate" timestamp(3) without time zone,
    "clientId" text NOT NULL,
    "caseId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "commissionPercent" numeric(5,2),
    "fileName" text,
    "fileStorageKey" text,
    "responsibleEmployeeId" text
);


--
-- Name: document_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.document_versions (
    id text NOT NULL,
    "documentId" text NOT NULL,
    version integer NOT NULL,
    "storageKey" text NOT NULL,
    "sizeBytes" integer,
    checksum text,
    "uploadedById" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    comment text,
    "mimeType" text
);


--
-- Name: documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.documents (
    id text NOT NULL,
    title text NOT NULL,
    "storageKey" text NOT NULL,
    "mimeType" text,
    "sizeBytes" integer,
    checksum text,
    "currentVersion" integer DEFAULT 1 NOT NULL,
    "caseId" text,
    "contractId" text,
    "clientId" text,
    "uploadedById" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "accessLevel" public."DocumentAccess" DEFAULT 'OFFICE'::public."DocumentAccess" NOT NULL,
    "docType" text
);


--
-- Name: employees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employees (
    id text NOT NULL,
    "userId" text NOT NULL,
    "position" text,
    "hireDate" timestamp(3) without time zone,
    "officeId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "commissionPercent" numeric(5,2) DEFAULT 10 NOT NULL,
    education text,
    "experienceYears" integer,
    kind public."EmployeeKind" DEFAULT 'STAFF'::public."EmployeeKind" NOT NULL,
    specialization text,
    status public."EmployeeStatus" DEFAULT 'ACTIVE'::public."EmployeeStatus" NOT NULL,
    languages text[] DEFAULT ARRAY[]::text[]
);


--
-- Name: integrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.integrations (
    id text NOT NULL,
    key text NOT NULL,
    name text NOT NULL,
    "isEnabled" boolean DEFAULT false NOT NULL,
    config jsonb,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    type public."IntegrationType"
);


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.invoices (
    id text NOT NULL,
    number text NOT NULL,
    status public."InvoiceStatus" DEFAULT 'DRAFT'::public."InvoiceStatus" NOT NULL,
    amount numeric(14,2) NOT NULL,
    currency text DEFAULT 'UZS'::text NOT NULL,
    "issuedAt" timestamp(3) without time zone,
    "dueDate" timestamp(3) without time zone,
    "clientId" text NOT NULL,
    "caseId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone
);


--
-- Name: lawyers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.lawyers (
    id text NOT NULL,
    "userId" text NOT NULL,
    "licenseNumber" text,
    specialization text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone
);


--
-- Name: login_attempts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.login_attempts (
    id text NOT NULL,
    identifier text NOT NULL,
    ip text,
    "userAgent" text,
    success boolean NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.messages (
    id text NOT NULL,
    "chatId" text NOT NULL,
    "senderId" text NOT NULL,
    body text NOT NULL,
    "editedAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "attachmentMime" text,
    "attachmentName" text,
    "attachmentStorageKey" text
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id text NOT NULL,
    "userId" text NOT NULL,
    channel public."NotificationChannel" NOT NULL,
    title text NOT NULL,
    body text NOT NULL,
    "isRead" boolean DEFAULT false NOT NULL,
    "readAt" timestamp(3) without time zone,
    "sentAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    event text
);


--
-- Name: offices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.offices (
    id text NOT NULL,
    name text NOT NULL,
    address text,
    "regionId" text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: partner_organizations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.partner_organizations (
    id text NOT NULL,
    name text NOT NULL,
    "logoStorageKey" text,
    description text,
    contacts jsonb,
    "contractNumber" text,
    "contractEndsAt" timestamp(3) without time zone,
    services text[] DEFAULT ARRAY[]::text[],
    status public."PartnerStatus" DEFAULT 'ACTIVE'::public."PartnerStatus" NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payments (
    id text NOT NULL,
    amount numeric(14,2) NOT NULL,
    currency text DEFAULT 'UZS'::text NOT NULL,
    status public."PaymentStatus" DEFAULT 'PENDING'::public."PaymentStatus" NOT NULL,
    method public."PaymentMethod",
    "paidAt" timestamp(3) without time zone,
    "clientId" text NOT NULL,
    "caseId" text,
    "invoiceId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    category public."PaymentCategory" DEFAULT 'SERVICES'::public."PaymentCategory" NOT NULL,
    comment text,
    "contractId" text,
    direction public."PaymentDirection" DEFAULT 'INCOME'::public."PaymentDirection" NOT NULL,
    "providerRef" text
);


--
-- Name: payouts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payouts (
    id text NOT NULL,
    "employeeId" text NOT NULL,
    amount numeric(14,2) NOT NULL,
    currency text DEFAULT 'UZS'::text NOT NULL,
    status public."PaymentStatus" DEFAULT 'PENDING'::public."PaymentStatus" NOT NULL,
    "periodFrom" timestamp(3) without time zone,
    "periodTo" timestamp(3) without time zone,
    comment text,
    "paidAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permissions (
    id text NOT NULL,
    key text NOT NULL,
    resource text NOT NULL,
    action text NOT NULL,
    description text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.profiles (
    id text NOT NULL,
    "userId" text NOT NULL,
    "firstName" text NOT NULL,
    "lastName" text NOT NULL,
    "middleName" text,
    "avatarUrl" text,
    "birthDate" timestamp(3) without time zone,
    address text,
    bio text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: queue_entries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.queue_entries (
    id text NOT NULL,
    date timestamp(3) without time zone NOT NULL,
    number integer NOT NULL,
    status public."QueueStatus" DEFAULT 'WAITING'::public."QueueStatus" NOT NULL,
    "clientId" text,
    "assigneeId" text,
    "officeId" text,
    "appointmentId" text,
    "joinedAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "calledAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.refresh_tokens (
    id text NOT NULL,
    "userId" text NOT NULL,
    "tokenHash" text NOT NULL,
    "familyId" text NOT NULL,
    ip text,
    "userAgent" text,
    label text,
    "expiresAt" timestamp(3) without time zone NOT NULL,
    "lastUsedAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "revokedAt" timestamp(3) without time zone,
    "replacedByHash" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: regions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.regions (
    id text NOT NULL,
    name text NOT NULL,
    code text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role_permissions (
    "roleId" text NOT NULL,
    "permissionId" text NOT NULL
);


--
-- Name: roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roles (
    id text NOT NULL,
    key text NOT NULL,
    name text NOT NULL,
    description text,
    "isSystem" boolean DEFAULT true NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: schedules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schedules (
    id text NOT NULL,
    "userId" text NOT NULL,
    "dayOfWeek" integer NOT NULL,
    "startTime" text NOT NULL,
    "endTime" text NOT NULL,
    "isActive" boolean DEFAULT true NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: services; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.services (
    id text NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    description text,
    "basePrice" numeric(14,2),
    "isActive" boolean DEFAULT true NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    category public."ServiceCategory" DEFAULT 'LEGAL'::public."ServiceCategory" NOT NULL,
    "sortOrder" integer DEFAULT 0 NOT NULL
);


--
-- Name: settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.settings (
    id text NOT NULL,
    key text NOT NULL,
    value jsonb NOT NULL,
    scope text DEFAULT 'GLOBAL'::text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tasks (
    id text NOT NULL,
    title text NOT NULL,
    description text,
    status public."TaskStatus" DEFAULT 'TODO'::public."TaskStatus" NOT NULL,
    priority public."TaskPriority" DEFAULT 'MEDIUM'::public."TaskPriority" NOT NULL,
    "dueDate" timestamp(3) without time zone,
    "assigneeId" text,
    "caseId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "authorId" text,
    "clientId" text
);


--
-- Name: time_off; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.time_off (
    id text NOT NULL,
    "userId" text NOT NULL,
    type public."TimeOffType" DEFAULT 'VACATION'::public."TimeOffType" NOT NULL,
    "startAt" timestamp(3) without time zone NOT NULL,
    "endAt" timestamp(3) without time zone NOT NULL,
    reason text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: timeline_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.timeline_events (
    id text NOT NULL,
    "clientId" text NOT NULL,
    type public."TimelineEventType" NOT NULL,
    title text NOT NULL,
    description text,
    "actorId" text,
    meta jsonb,
    "occurredAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: user_preferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_preferences (
    id text NOT NULL,
    "userId" text NOT NULL,
    locale text DEFAULT 'uz'::text NOT NULL,
    theme text DEFAULT 'system'::text NOT NULL,
    timezone text DEFAULT 'Asia/Tashkent'::text NOT NULL,
    "dateFormat" text DEFAULT 'dd.MM.yyyy'::text NOT NULL,
    "notifyInApp" boolean DEFAULT true NOT NULL,
    "notifyEmail" boolean DEFAULT true NOT NULL,
    "notifySms" boolean DEFAULT false NOT NULL,
    "notifyPush" boolean DEFAULT false NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_roles (
    "userId" text NOT NULL,
    "roleId" text NOT NULL,
    "assignedAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id text NOT NULL,
    email text NOT NULL,
    phone text,
    "passwordHash" text NOT NULL,
    type public."UserType" NOT NULL,
    "isActive" boolean DEFAULT true NOT NULL,
    locale text DEFAULT 'uz'::text NOT NULL,
    "lastLoginAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "deletedAt" timestamp(3) without time zone,
    "emailVerifiedAt" timestamp(3) without time zone,
    "phoneVerifiedAt" timestamp(3) without time zone,
    "failedLoginCount" integer DEFAULT 0 NOT NULL,
    "lockedUntil" timestamp(3) without time zone,
    "twoFactorEnabled" boolean DEFAULT false NOT NULL,
    "twoFactorSecret" text,
    "regionId" text,
    "officeId" text
);


--
-- Name: verification_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.verification_tokens (
    id text NOT NULL,
    "userId" text NOT NULL,
    type public."VerificationTokenType" NOT NULL,
    "tokenHash" text NOT NULL,
    "expiresAt" timestamp(3) without time zone NOT NULL,
    "consumedAt" timestamp(3) without time zone,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: _prisma_migrations _prisma_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public._prisma_migrations
    ADD CONSTRAINT _prisma_migrations_pkey PRIMARY KEY (id);


--
-- Name: advocates advocates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.advocates
    ADD CONSTRAINT advocates_pkey PRIMARY KEY (id);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: case_notes case_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.case_notes
    ADD CONSTRAINT case_notes_pkey PRIMARY KEY (id);


--
-- Name: case_services case_services_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.case_services
    ADD CONSTRAINT case_services_pkey PRIMARY KEY (id);


--
-- Name: cases cases_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_pkey PRIMARY KEY (id);


--
-- Name: chat_members chat_members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_members
    ADD CONSTRAINT chat_members_pkey PRIMARY KEY (id);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (id);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: contracts contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pkey PRIMARY KEY (id);


--
-- Name: document_versions document_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT document_versions_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: integrations integrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.integrations
    ADD CONSTRAINT integrations_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: lawyers lawyers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lawyers
    ADD CONSTRAINT lawyers_pkey PRIMARY KEY (id);


--
-- Name: login_attempts login_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.login_attempts
    ADD CONSTRAINT login_attempts_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: offices offices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.offices
    ADD CONSTRAINT offices_pkey PRIMARY KEY (id);


--
-- Name: partner_organizations partner_organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.partner_organizations
    ADD CONSTRAINT partner_organizations_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: payouts payouts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payouts
    ADD CONSTRAINT payouts_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: queue_entries queue_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.queue_entries
    ADD CONSTRAINT queue_entries_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY ("roleId", "permissionId");


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: time_off time_off_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_off
    ADD CONSTRAINT time_off_pkey PRIMARY KEY (id);


--
-- Name: timeline_events timeline_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeline_events
    ADD CONSTRAINT timeline_events_pkey PRIMARY KEY (id);


--
-- Name: user_preferences user_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY ("userId", "roleId");


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: verification_tokens verification_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verification_tokens
    ADD CONSTRAINT verification_tokens_pkey PRIMARY KEY (id);


--
-- Name: advocates_barNumber_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "advocates_barNumber_key" ON public.advocates USING btree ("barNumber");


--
-- Name: advocates_userId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "advocates_userId_key" ON public.advocates USING btree ("userId");


--
-- Name: appointments_assigneeId_startAt_endAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "appointments_assigneeId_startAt_endAt_idx" ON public.appointments USING btree ("assigneeId", "startAt", "endAt");


--
-- Name: appointments_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "appointments_caseId_idx" ON public.appointments USING btree ("caseId");


--
-- Name: appointments_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "appointments_clientId_idx" ON public.appointments USING btree ("clientId");


--
-- Name: appointments_startAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "appointments_startAt_idx" ON public.appointments USING btree ("startAt");


--
-- Name: audit_logs_actorId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "audit_logs_actorId_idx" ON public.audit_logs USING btree ("actorId");


--
-- Name: audit_logs_createdAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "audit_logs_createdAt_idx" ON public.audit_logs USING btree ("createdAt");


--
-- Name: audit_logs_entity_entityId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "audit_logs_entity_entityId_idx" ON public.audit_logs USING btree (entity, "entityId");


--
-- Name: case_notes_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "case_notes_caseId_idx" ON public.case_notes USING btree ("caseId");


--
-- Name: case_services_caseId_serviceId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "case_services_caseId_serviceId_key" ON public.case_services USING btree ("caseId", "serviceId");


--
-- Name: case_services_serviceId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "case_services_serviceId_idx" ON public.case_services USING btree ("serviceId");


--
-- Name: cases_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "cases_clientId_idx" ON public.cases USING btree ("clientId");


--
-- Name: cases_deletedAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "cases_deletedAt_idx" ON public.cases USING btree ("deletedAt");


--
-- Name: cases_lawyerId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "cases_lawyerId_idx" ON public.cases USING btree ("lawyerId");


--
-- Name: cases_number_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX cases_number_key ON public.cases USING btree (number);


--
-- Name: cases_officeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "cases_officeId_idx" ON public.cases USING btree ("officeId");


--
-- Name: cases_priority_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cases_priority_idx ON public.cases USING btree (priority);


--
-- Name: cases_responsibleEmployeeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "cases_responsibleEmployeeId_idx" ON public.cases USING btree ("responsibleEmployeeId");


--
-- Name: cases_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cases_status_idx ON public.cases USING btree (status);


--
-- Name: chat_members_chatId_userId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "chat_members_chatId_userId_key" ON public.chat_members USING btree ("chatId", "userId");


--
-- Name: chat_members_userId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "chat_members_userId_idx" ON public.chat_members USING btree ("userId");


--
-- Name: chats_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "chats_caseId_idx" ON public.chats USING btree ("caseId");


--
-- Name: chats_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "chats_clientId_idx" ON public.chats USING btree ("clientId");


--
-- Name: clients_code_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX clients_code_key ON public.clients USING btree (code);


--
-- Name: clients_deletedAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "clients_deletedAt_idx" ON public.clients USING btree ("deletedAt");


--
-- Name: clients_regionId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "clients_regionId_idx" ON public.clients USING btree ("regionId");


--
-- Name: clients_responsibleEmployeeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "clients_responsibleEmployeeId_idx" ON public.clients USING btree ("responsibleEmployeeId");


--
-- Name: clients_userId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "clients_userId_key" ON public.clients USING btree ("userId");


--
-- Name: contracts_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "contracts_caseId_idx" ON public.contracts USING btree ("caseId");


--
-- Name: contracts_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "contracts_clientId_idx" ON public.contracts USING btree ("clientId");


--
-- Name: contracts_number_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX contracts_number_key ON public.contracts USING btree (number);


--
-- Name: contracts_responsibleEmployeeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "contracts_responsibleEmployeeId_idx" ON public.contracts USING btree ("responsibleEmployeeId");


--
-- Name: contracts_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX contracts_status_idx ON public.contracts USING btree (status);


--
-- Name: document_versions_documentId_version_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "document_versions_documentId_version_key" ON public.document_versions USING btree ("documentId", version);


--
-- Name: documents_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "documents_caseId_idx" ON public.documents USING btree ("caseId");


--
-- Name: documents_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "documents_clientId_idx" ON public.documents USING btree ("clientId");


--
-- Name: documents_contractId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "documents_contractId_idx" ON public.documents USING btree ("contractId");


--
-- Name: employees_kind_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX employees_kind_idx ON public.employees USING btree (kind);


--
-- Name: employees_officeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "employees_officeId_idx" ON public.employees USING btree ("officeId");


--
-- Name: employees_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX employees_status_idx ON public.employees USING btree (status);


--
-- Name: employees_userId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "employees_userId_key" ON public.employees USING btree ("userId");


--
-- Name: integrations_key_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX integrations_key_key ON public.integrations USING btree (key);


--
-- Name: invoices_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "invoices_caseId_idx" ON public.invoices USING btree ("caseId");


--
-- Name: invoices_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "invoices_clientId_idx" ON public.invoices USING btree ("clientId");


--
-- Name: invoices_number_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX invoices_number_key ON public.invoices USING btree (number);


--
-- Name: invoices_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX invoices_status_idx ON public.invoices USING btree (status);


--
-- Name: lawyers_licenseNumber_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "lawyers_licenseNumber_key" ON public.lawyers USING btree ("licenseNumber");


--
-- Name: lawyers_userId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "lawyers_userId_key" ON public.lawyers USING btree ("userId");


--
-- Name: login_attempts_identifier_createdAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "login_attempts_identifier_createdAt_idx" ON public.login_attempts USING btree (identifier, "createdAt");


--
-- Name: login_attempts_ip_createdAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "login_attempts_ip_createdAt_idx" ON public.login_attempts USING btree (ip, "createdAt");


--
-- Name: messages_chatId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "messages_chatId_idx" ON public.messages USING btree ("chatId");


--
-- Name: messages_senderId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "messages_senderId_idx" ON public.messages USING btree ("senderId");


--
-- Name: notifications_isRead_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "notifications_isRead_idx" ON public.notifications USING btree ("isRead");


--
-- Name: notifications_userId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "notifications_userId_idx" ON public.notifications USING btree ("userId");


--
-- Name: offices_regionId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "offices_regionId_idx" ON public.offices USING btree ("regionId");


--
-- Name: partner_organizations_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX partner_organizations_status_idx ON public.partner_organizations USING btree (status);


--
-- Name: payments_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "payments_caseId_idx" ON public.payments USING btree ("caseId");


--
-- Name: payments_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "payments_clientId_idx" ON public.payments USING btree ("clientId");


--
-- Name: payments_contractId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "payments_contractId_idx" ON public.payments USING btree ("contractId");


--
-- Name: payments_direction_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX payments_direction_idx ON public.payments USING btree (direction);


--
-- Name: payments_invoiceId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "payments_invoiceId_idx" ON public.payments USING btree ("invoiceId");


--
-- Name: payments_paidAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "payments_paidAt_idx" ON public.payments USING btree ("paidAt");


--
-- Name: payments_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX payments_status_idx ON public.payments USING btree (status);


--
-- Name: payouts_employeeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "payouts_employeeId_idx" ON public.payouts USING btree ("employeeId");


--
-- Name: payouts_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX payouts_status_idx ON public.payouts USING btree (status);


--
-- Name: permissions_key_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX permissions_key_key ON public.permissions USING btree (key);


--
-- Name: permissions_resource_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX permissions_resource_idx ON public.permissions USING btree (resource);


--
-- Name: profiles_userId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "profiles_userId_key" ON public.profiles USING btree ("userId");


--
-- Name: queue_entries_appointmentId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "queue_entries_appointmentId_key" ON public.queue_entries USING btree ("appointmentId");


--
-- Name: queue_entries_date_assigneeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "queue_entries_date_assigneeId_idx" ON public.queue_entries USING btree (date, "assigneeId");


--
-- Name: queue_entries_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX queue_entries_status_idx ON public.queue_entries USING btree (status);


--
-- Name: refresh_tokens_familyId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "refresh_tokens_familyId_idx" ON public.refresh_tokens USING btree ("familyId");


--
-- Name: refresh_tokens_userId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "refresh_tokens_userId_idx" ON public.refresh_tokens USING btree ("userId");


--
-- Name: regions_code_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX regions_code_key ON public.regions USING btree (code);


--
-- Name: role_permissions_permissionId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "role_permissions_permissionId_idx" ON public.role_permissions USING btree ("permissionId");


--
-- Name: roles_key_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX roles_key_key ON public.roles USING btree (key);


--
-- Name: schedules_userId_dayOfWeek_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "schedules_userId_dayOfWeek_key" ON public.schedules USING btree ("userId", "dayOfWeek");


--
-- Name: services_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX services_category_idx ON public.services USING btree (category);


--
-- Name: services_code_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX services_code_key ON public.services USING btree (code);


--
-- Name: services_isActive_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "services_isActive_idx" ON public.services USING btree ("isActive");


--
-- Name: settings_key_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX settings_key_key ON public.settings USING btree (key);


--
-- Name: tasks_assigneeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "tasks_assigneeId_idx" ON public.tasks USING btree ("assigneeId");


--
-- Name: tasks_caseId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "tasks_caseId_idx" ON public.tasks USING btree ("caseId");


--
-- Name: tasks_clientId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "tasks_clientId_idx" ON public.tasks USING btree ("clientId");


--
-- Name: tasks_dueDate_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "tasks_dueDate_idx" ON public.tasks USING btree ("dueDate");


--
-- Name: tasks_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX tasks_status_idx ON public.tasks USING btree (status);


--
-- Name: time_off_userId_startAt_endAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "time_off_userId_startAt_endAt_idx" ON public.time_off USING btree ("userId", "startAt", "endAt");


--
-- Name: timeline_events_clientId_occurredAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "timeline_events_clientId_occurredAt_idx" ON public.timeline_events USING btree ("clientId", "occurredAt");


--
-- Name: user_preferences_userId_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "user_preferences_userId_key" ON public.user_preferences USING btree ("userId");


--
-- Name: user_roles_roleId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "user_roles_roleId_idx" ON public.user_roles USING btree ("roleId");


--
-- Name: users_deletedAt_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "users_deletedAt_idx" ON public.users USING btree ("deletedAt");


--
-- Name: users_email_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);


--
-- Name: users_officeId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "users_officeId_idx" ON public.users USING btree ("officeId");


--
-- Name: users_phone_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX users_phone_key ON public.users USING btree (phone);


--
-- Name: users_regionId_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "users_regionId_idx" ON public.users USING btree ("regionId");


--
-- Name: verification_tokens_userId_type_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "verification_tokens_userId_type_idx" ON public.verification_tokens USING btree ("userId", type);


--
-- Name: advocates advocates_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.advocates
    ADD CONSTRAINT "advocates_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: appointments appointments_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT "appointments_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: case_notes case_notes_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.case_notes
    ADD CONSTRAINT "case_notes_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: case_services case_services_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.case_services
    ADD CONSTRAINT "case_services_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: case_services case_services_serviceId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.case_services
    ADD CONSTRAINT "case_services_serviceId_fkey" FOREIGN KEY ("serviceId") REFERENCES public.services(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: cases cases_advocateId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT "cases_advocateId_fkey" FOREIGN KEY ("advocateId") REFERENCES public.advocates(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: cases cases_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT "cases_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: cases cases_lawyerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT "cases_lawyerId_fkey" FOREIGN KEY ("lawyerId") REFERENCES public.lawyers(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: cases cases_officeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT "cases_officeId_fkey" FOREIGN KEY ("officeId") REFERENCES public.offices(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: cases cases_responsibleEmployeeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT "cases_responsibleEmployeeId_fkey" FOREIGN KEY ("responsibleEmployeeId") REFERENCES public.employees(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: chat_members chat_members_chatId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_members
    ADD CONSTRAINT "chat_members_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES public.chats(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: chat_members chat_members_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_members
    ADD CONSTRAINT "chat_members_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: chats chats_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT "chats_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: chats chats_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT "chats_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: clients clients_regionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT "clients_regionId_fkey" FOREIGN KEY ("regionId") REFERENCES public.regions(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: clients clients_responsibleEmployeeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT "clients_responsibleEmployeeId_fkey" FOREIGN KEY ("responsibleEmployeeId") REFERENCES public.employees(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: clients clients_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT "clients_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: contracts contracts_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT "contracts_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: contracts contracts_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT "contracts_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: contracts contracts_responsibleEmployeeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT "contracts_responsibleEmployeeId_fkey" FOREIGN KEY ("responsibleEmployeeId") REFERENCES public.employees(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: document_versions document_versions_documentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.document_versions
    ADD CONSTRAINT "document_versions_documentId_fkey" FOREIGN KEY ("documentId") REFERENCES public.documents(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: documents documents_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT "documents_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: documents documents_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT "documents_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: documents documents_contractId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT "documents_contractId_fkey" FOREIGN KEY ("contractId") REFERENCES public.contracts(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: employees employees_officeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT "employees_officeId_fkey" FOREIGN KEY ("officeId") REFERENCES public.offices(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: employees employees_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT "employees_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: invoices invoices_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT "invoices_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: invoices invoices_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT "invoices_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: lawyers lawyers_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.lawyers
    ADD CONSTRAINT "lawyers_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: messages messages_chatId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT "messages_chatId_fkey" FOREIGN KEY ("chatId") REFERENCES public.chats(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: messages messages_senderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT "messages_senderId_fkey" FOREIGN KEY ("senderId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: notifications notifications_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT "notifications_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: offices offices_regionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.offices
    ADD CONSTRAINT "offices_regionId_fkey" FOREIGN KEY ("regionId") REFERENCES public.regions(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: payments payments_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT "payments_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: payments payments_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT "payments_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: payments payments_contractId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT "payments_contractId_fkey" FOREIGN KEY ("contractId") REFERENCES public.contracts(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: payments payments_invoiceId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT "payments_invoiceId_fkey" FOREIGN KEY ("invoiceId") REFERENCES public.invoices(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: payouts payouts_employeeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payouts
    ADD CONSTRAINT "payouts_employeeId_fkey" FOREIGN KEY ("employeeId") REFERENCES public.employees(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: profiles profiles_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT "profiles_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: queue_entries queue_entries_appointmentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.queue_entries
    ADD CONSTRAINT "queue_entries_appointmentId_fkey" FOREIGN KEY ("appointmentId") REFERENCES public.appointments(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: refresh_tokens refresh_tokens_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT "refresh_tokens_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permissionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT "role_permissions_permissionId_fkey" FOREIGN KEY ("permissionId") REFERENCES public.permissions(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_roleId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT "role_permissions_roleId_fkey" FOREIGN KEY ("roleId") REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: schedules schedules_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT "schedules_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tasks tasks_caseId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT "tasks_caseId_fkey" FOREIGN KEY ("caseId") REFERENCES public.cases(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: tasks tasks_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT "tasks_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: time_off time_off_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.time_off
    ADD CONSTRAINT "time_off_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: timeline_events timeline_events_clientId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.timeline_events
    ADD CONSTRAINT "timeline_events_clientId_fkey" FOREIGN KEY ("clientId") REFERENCES public.clients(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_preferences user_preferences_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT "user_preferences_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_roles user_roles_roleId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT "user_roles_roleId_fkey" FOREIGN KEY ("roleId") REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_roles user_roles_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT "user_roles_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: users users_officeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT "users_officeId_fkey" FOREIGN KEY ("officeId") REFERENCES public.offices(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: users users_regionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT "users_regionId_fkey" FOREIGN KEY ("regionId") REFERENCES public.regions(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: verification_tokens verification_tokens_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verification_tokens
    ADD CONSTRAINT "verification_tokens_userId_fkey" FOREIGN KEY ("userId") REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


