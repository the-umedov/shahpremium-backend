# ShahPremium API (Python porti)

Bu — `E:\shahpremiumuz\apps\api` (NestJS + Prisma) backendining **to'liq Python portidir**:
FastAPI + SQLAlchemy 2.0 (async) + Alembic + PostgreSQL. Asl loyihaga hech narsa
o'zgartirilmagan — bu butunlay mustaqil, yangi papka.

## Muhim ogohlantirish: manba kodning holati

Portlashni boshlashda asl loyihada **`src/` (TypeScript manba) va `prisma/schema.prisma`
umuman topilmadi** — faqat `apps/api/dist/**` (kompilyatsiya qilingan JS) va mos
`*.d.ts` fayllar qolgan edi. Shuning uchun:

- **Ma'lumotlar bazasi sxemasi** (`app/models/models.py`, `app/models/enums.py`)
  `this.prisma.<model>.<method>({where/select/include/data})` chaqiruvlarini butun
  kod bo'ylab o'qib, qayta tiklandi. Aksariyat jadval/maydonlar aniq dalil bilan
  tasdiqlangan; ba'zi enum a'zolari (masalan `ContractStatus`, `InvoiceStatus`,
  `ServiceCategory`, `PaymentCategory`) kodda hech qachon literal ko'rinishda
  uchramagan — ular domen bo'yicha oqilona taxmin, va shu haqda fayl ichida
  aniq izoh qoldirilgan.
- **RBAC ruxsatlar ro'yxati** (`scripts/seed.py`ning `PERMISSIONS`) — barcha
  kontrollerlardagi `@RequirePermissions(...)` dekoratorlarini grep qilib,
  **to'liq va aniq** tiklandi (taxmin emas).
- **Rol → ruxsat mapping** va **demo seed** — asl `prisma/seed.ts` topilmagani
  uchun domen bo'yicha oqilona taxmin (`scripts/seed.py` ichida izohlangan).

Productionga o'tishdan oldin ushbu taxminlarni (ayniqsa enum qiymatlari va
rol-ruxsat mappingini) haqiqiy biznes talablari bilan solishtirib tekshiring.

## Texnologiyalar

| Qatlam | Texnologiya |
|--------|-------------|
| Backend | FastAPI, Pydantic v2, uvicorn |
| Database | PostgreSQL + SQLAlchemy 2.0 (async, asyncpg) + Alembic |
| Auth | JWT (access+refresh rotation), argon2, RBAC + object-level scoping, TOTP 2FA |
| Realtime | python-socketio (chat), ASGI orqali FastAPI bilan bir jarayonda |
| Storage | Local disk (S3/MinIO-mos interfeys), HMAC bilan imzolangan vaqtinchalik havolalar |
| Reports | openpyxl (Excel), reportlab (PDF), CSV |

## Struktura

```
app/
  core/       config, database, security (JWT/argon2), RBAC, pagination,
              storage, audit/CSRF middleware, exception handlers
  models/     SQLAlchemy modellar (models.py) + enumlar (enums.py)
  modules/    har bir domen moduli: authentication, users, roles, permissions,
              employees, lawyers*, advocates*, clients, regions, offices,
              services, cases, contracts, documents, appointments, calendar*,
              tasks, payments, reports, notifications, chat, audit,
              integrations, settings, dashboard
              (* — asl loyihada ham bo'sh stub edi, shu holicha saqlandi)
alembic/      migratsiyalar
scripts/      seed.py — demo rol/ruxsat/foydalanuvchilar
```

Har bir modul: `schemas.py` (Pydantic), `service.py` (async biznes-mantiq),
`router.py` (`router = APIRouter(...)`).

## Ishga tushirish

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env      # qiymatlarni to'ldiring (DATABASE_URL va h.k.)

# Baza
.venv\Scripts\alembic revision --autogenerate -m "init"
.venv\Scripts\alembic upgrade head
.venv\Scripts\python -m scripts.seed     # demo rol/ruxsat/foydalanuvchilar

# Ishga tushirish
.venv\Scripts\uvicorn app.main:app --reload --port 4000
```

Swagger: `http://localhost:4000/api/v1/docs`... aslida OpenAPI JSON `/openapi.json`
orqali ham ochiladi (FastAPI standart `/docs` yo'lida — `API_PREFIX` bilan
mos ravishda tekshiring).

Demo login: `admin@demo.shahpremium.uz` / `Password123!`
(barcha demo rollar: superadmin/admin/lawyer/accountant/manager/client @demo.shahpremium.uz).

## Tekshirilgan holat

- `python -m py_compile` — barcha fayllar sintaksis jihatdan toza.
- `python -c "import app.main"` — butun FastAPI ilova (115 ta route) muvaffaqiyatli
  yig'iladi, barcha modul routerlari to'g'ri ulanadi.
- `app.openapi()` — OpenAPI sxemasi xatosiz generatsiya qilinadi (82 ta path).
- **Haqiqiy PostgreSQL bazasiga ulanib CRUD oqimlari amalda sinalmagan** — buni
  `DATABASE_URL`ni sozlab, Alembic migratsiyasini ishga tushirib, keyin
  qo'lda yoki test bilan tekshiring.
