from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.health import router as health_router
from app.core.audit import AuditMiddleware
from app.core.config import get_settings
from app.core.csrf import CsrfMiddleware
from app.core.deps import get_current_user
from app.core.exceptions import http_exception_handler, unhandled_exception_handler
from app.core.logging import configure_logging

# Domen routerlari (app.module.ts importlari ekvivalenti)
from app.modules.advocates.router import router as advocates_router
from app.modules.appointments.router import router as appointments_router
from app.modules.audit.router import router as audit_router
from app.modules.authentication.router import router as authentication_router
from app.modules.calendar.router import router as calendar_router
from app.modules.cases.router import router as cases_router
from app.modules.chat.router import router as chat_router
from app.modules.clients.router import router as clients_router
from app.modules.contracts.router import router as contracts_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.documents.router import public_router as documents_public_router
from app.modules.documents.router import router as documents_router
from app.modules.employees.router import router as employees_router
from app.modules.integrations.router import router as integrations_router
from app.modules.lawyers.router import router as lawyers_router
from app.modules.notifications.router import router as notifications_router
from app.modules.offices.router import router as offices_router
from app.modules.payments.router import router as payments_router
from app.modules.permissions.router import router as permissions_router
from app.modules.regions.router import router as regions_router
from app.modules.reports.router import router as reports_router
from app.modules.roles.router import router as roles_router
from app.modules.services.router import router as services_router
from app.modules.settings.router import router as settings_router
from app.modules.tasks.router import router as tasks_router
from app.modules.users.router import router as users_router

settings = get_settings()
configure_logging()

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="ShahPremium API",
    description="Yuridik SaaS platforma REST API",
    version="1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(AuditMiddleware)
app.add_middleware(CsrfMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_prefix

# Public: health + auth login/register/refresh (bu routerlar ichida public endpointlar
# alohida belgilangan, qolganlari get_current_user talab qiladi — JwtAuthGuard ekvivalenti)
app.include_router(health_router, prefix=prefix)
app.include_router(authentication_router, prefix=f"{prefix}/auth")

_protected = Depends(get_current_user)

app.include_router(users_router, prefix=f"{prefix}/users", dependencies=[_protected])
app.include_router(roles_router, prefix=f"{prefix}/roles", dependencies=[_protected])
app.include_router(permissions_router, prefix=f"{prefix}/permissions", dependencies=[_protected])
app.include_router(employees_router, prefix=f"{prefix}/employees", dependencies=[_protected])
app.include_router(lawyers_router, prefix=f"{prefix}/lawyers", dependencies=[_protected])
app.include_router(advocates_router, prefix=f"{prefix}/advocates", dependencies=[_protected])
app.include_router(clients_router, prefix=f"{prefix}/clients", dependencies=[_protected])
app.include_router(regions_router, prefix=f"{prefix}/regions", dependencies=[_protected])
app.include_router(offices_router, prefix=f"{prefix}/offices", dependencies=[_protected])
app.include_router(services_router, prefix=f"{prefix}/services", dependencies=[_protected])
app.include_router(cases_router, prefix=f"{prefix}/cases", dependencies=[_protected])
app.include_router(contracts_router, prefix=f"{prefix}/contracts", dependencies=[_protected])
app.include_router(documents_public_router, prefix=f"{prefix}/documents")
app.include_router(documents_router, prefix=f"{prefix}/documents", dependencies=[_protected])
app.include_router(appointments_router, prefix=f"{prefix}/appointments", dependencies=[_protected])
app.include_router(calendar_router, prefix=f"{prefix}/calendar", dependencies=[_protected])
app.include_router(tasks_router, prefix=f"{prefix}/tasks", dependencies=[_protected])
app.include_router(payments_router, prefix=f"{prefix}/payments", dependencies=[_protected])
app.include_router(reports_router, prefix=f"{prefix}/reports", dependencies=[_protected])
app.include_router(notifications_router, prefix=f"{prefix}/notifications", dependencies=[_protected])
app.include_router(chat_router, prefix=f"{prefix}/chat", dependencies=[_protected])
app.include_router(audit_router, prefix=f"{prefix}/audit", dependencies=[_protected])
app.include_router(integrations_router, prefix=f"{prefix}/integrations", dependencies=[_protected])
app.include_router(settings_router, prefix=f"{prefix}/settings", dependencies=[_protected])
app.include_router(dashboard_router, prefix=f"{prefix}/dashboard", dependencies=[_protected])

# Realtime chat (socket.io) — app.modules.chat.socket_app da ASGI sifatida eksport qilinadi
from app.modules.chat.socket_app import sio_asgi_app  # noqa: E402

app.mount("/socket.io", sio_asgi_app)
