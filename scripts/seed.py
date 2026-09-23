"""Demo ma'lumotlar bilan bazani to'ldiradi (roles/permissions/demo users).

MANBA: E:\\pgdata-shahpremium — asl Prisma-boshqaruvidagi PostgreSQL bazasining
HAQIQIY, ishlab turgan nusxasi (dev, prod'dan oldin qolgan). Quyidagi PERMISSIONS
(48 ta, taxmin emas — `select key from permissions order by key` bilan tekshirilgan),
rol nomlari (o'zbekcha) va ROLE_PERMISSIONS mapping'i shu haqiqiy baza
`roles`/`permissions`/`role_permissions` jadvallaridan to'g'ridan-to'g'ri o'qib
olingan va tasdiqlangan (LAWYER/ADVOCATE = 17 ta bir xil ruxsat, MANAGER = 18,
ACCOUNTANT = 12, CLIENT = 8, SUPER_ADMIN/ADMIN = barcha 48 ta).

Bu baza allaqachon 6 ta demo foydalanuvchi (haqiqiy parol hash'lari bilan),
7 ta rol va 48 ta ruxsat bilan to'ldirilgan — shu sababli bu skript to'liq
IDEMPOTENT: har bir yozuv oldin mavjudligi tekshiriladi, mavjud bo'lsa
o'tkazib yuboriladi (parollar hech qachon qayta yozilmaydi).

Ishga tushirish:
    python -m scripts.seed
"""

import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.enums import RoleKey, UserType
from app.models.models import Permission, Role, RolePermission, User, UserProfile, UserRole

# `select key from permissions order by key` — haqiqiy bazadan tasdiqlangan, 48 ta.
PERMISSIONS: list[str] = [
    "appointments.manage",
    "audit.read",
    "calendar.read",
    "cases.create",
    "cases.delete",
    "cases.read",
    "cases.update",
    "chat.use",
    "clients.create",
    "clients.delete",
    "clients.read",
    "clients.update",
    "contracts.create",
    "contracts.delete",
    "contracts.read",
    "contracts.update",
    "dashboard.read",
    "documents.delete",
    "documents.read",
    "documents.update",
    "documents.upload",
    "employees.create",
    "employees.delete",
    "employees.read",
    "employees.update",
    "integrations.manage",
    "invoices.create",
    "invoices.read",
    "invoices.update",
    "notifications.read",
    "offices.manage",
    "payments.create",
    "payments.read",
    "payments.update",
    "regions.manage",
    "reports.export",
    "reports.read",
    "roles.manage",
    "services.manage",
    "settings.manage",
    "tasks.create",
    "tasks.delete",
    "tasks.read",
    "tasks.update",
    "users.create",
    "users.delete",
    "users.read",
    "users.update",
]

ALL = PERMISSIONS

# Haqiqiy `roles.name` qiymatlari (o'zbekcha), bazadan tasdiqlangan.
ROLE_NAMES: dict[RoleKey, str] = {
    RoleKey.SUPER_ADMIN: "Toʻliq nazorat (tizim egasi)",
    RoleKey.ADMIN: "Administrator",
    RoleKey.LAWYER: "Yurist",
    RoleKey.ADVOCATE: "Advokat",
    RoleKey.ACCOUNTANT: "Buxgalter",
    RoleKey.MANAGER: "Menejer",
    RoleKey.CLIENT: "Mijoz",
}

# Haqiqiy `role_permissions` jadvalidan tasdiqlangan rol->ruxsat mapping (taxmin emas).
_LAWYER_ADVOCATE_SET = [
    "appointments.manage", "calendar.read", "cases.create", "cases.read", "cases.update",
    "chat.use", "clients.read", "contracts.read", "dashboard.read", "documents.read",
    "documents.update", "documents.upload", "notifications.read", "reports.read",
    "tasks.create", "tasks.read", "tasks.update",
]

ROLE_PERMISSIONS: dict[RoleKey, list[str]] = {
    RoleKey.SUPER_ADMIN: ALL,
    RoleKey.ADMIN: ALL,
    RoleKey.MANAGER: [
        "appointments.manage", "calendar.read", "cases.read", "cases.update", "chat.use",
        "clients.create", "clients.delete", "clients.read", "clients.update", "dashboard.read",
        "employees.read", "notifications.read", "reports.export", "reports.read",
        "tasks.create", "tasks.delete", "tasks.read", "tasks.update",
    ],
    RoleKey.ACCOUNTANT: [
        "clients.read", "contracts.read", "dashboard.read", "invoices.create", "invoices.read",
        "invoices.update", "notifications.read", "payments.create", "payments.read",
        "payments.update", "reports.export", "reports.read",
    ],
    RoleKey.LAWYER: _LAWYER_ADVOCATE_SET,
    RoleKey.ADVOCATE: _LAWYER_ADVOCATE_SET,
    RoleKey.CLIENT: [
        "appointments.manage", "cases.read", "chat.use", "contracts.read", "documents.read",
        "invoices.read", "notifications.read", "payments.read",
    ],
}

DEMO_PASSWORD = "Password123!"
DEMO_DOMAIN = "demo.shahpremium.uz"

# Haqiqiy bazada mavjud 6 ta demo hisob (parol hash'lari HAQIQIY — bu yerda qayta
# yaratilmaydi/yozilmaydi, faqat mavjud emas bo'lgan holatda — masalan bo'sh/yangi
# baza ustida ishga tushirilganda — yaratiladi). ADVOCATE uchun demo hisob YO'Q
# (haqiqiy bazada ham yo'q) — shu sababli bu ro'yxatga qo'shilmagan, atayin.
DEMO_USERS: list[tuple[str, UserType, RoleKey]] = [
    ("superadmin", UserType.EMPLOYEE, RoleKey.SUPER_ADMIN),
    ("admin", UserType.EMPLOYEE, RoleKey.ADMIN),
    ("manager", UserType.EMPLOYEE, RoleKey.MANAGER),
    ("accountant", UserType.EMPLOYEE, RoleKey.ACCOUNTANT),
    ("lawyer", UserType.LAWYER, RoleKey.LAWYER),
    ("client", UserType.CLIENT, RoleKey.CLIENT),
]


async def seed() -> None:
    async with SessionLocal() as db:
        permission_rows: dict[str, Permission] = {}
        for key in PERMISSIONS:
            resource, action = key.split(".", 1)
            existing = (await db.execute(select(Permission).where(Permission.key == key))).scalar_one_or_none()
            if existing:
                permission_rows[key] = existing
                continue
            perm = Permission(key=key, resource=resource, action=action)
            db.add(perm)
            permission_rows[key] = perm
        await db.flush()

        role_rows: dict[RoleKey, Role] = {}
        for role_key, perms in ROLE_PERMISSIONS.items():
            existing = (await db.execute(select(Role).where(Role.key == role_key))).scalar_one_or_none()
            role = existing or Role(key=role_key, name=ROLE_NAMES[role_key], is_system=True)
            if not existing:
                db.add(role)
                await db.flush()
            role_rows[role_key] = role

            existing_links = (
                await db.execute(select(RolePermission.permission_id).where(RolePermission.role_id == role.id))
            ).scalars().all()
            existing_ids = set(existing_links)
            for perm_key in perms:
                perm = permission_rows[perm_key]
                if perm.id not in existing_ids:
                    db.add(RolePermission(role_id=role.id, permission_id=perm.id))
        await db.flush()

        for local_part, user_type, role_key in DEMO_USERS:
            email = f"{local_part}@{DEMO_DOMAIN}"
            existing_user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
            if existing_user:
                # Foydalanuvchi allaqachon mavjud (haqiqiy parol hash'i bilan) — teginmaymiz.
                continue
            user = User(
                email=email,
                password_hash=hash_password(DEMO_PASSWORD),
                type=user_type,
                is_active=True,
            )
            db.add(user)
            await db.flush()
            db.add(UserProfile(user_id=user.id, first_name=local_part.title(), last_name="Demo"))
            db.add(UserRole(user_id=user.id, role_id=role_rows[role_key].id))

        await db.commit()
        print(
            f"Seed tugadi: {len(PERMISSIONS)} ruxsat, {len(ROLE_PERMISSIONS)} rol, "
            f"demo foydalanuvchilar (@{DEMO_DOMAIN}, mavjud bo'lmaganlari uchun parol: {DEMO_PASSWORD})."
        )


if __name__ == "__main__":
    asyncio.run(seed())
