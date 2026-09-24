"""Yangi (bo'sh) Render/production PostgreSQL bazasini bir martalik tayyorlaydi:

1) db/schema.sql'ni qo'llaydi — barcha jadval/enum/FK/indekslarni yaratadi
   (E:\\pgdata-shahpremium dagi asl Prisma bazasidan olingan haqiqiy sxema).
2) scripts/seed.py chaqiriladi — 7 tizim roli, 48 ruxsat, 6 demo foydalanuvchi.
3) db/migrations/*.sql qo'llanadi (har safar, idempotent).
4) scripts/seed_geography.py — barcha viloyat va tumanlar (yetishmaganlari).

Idempotent: `users` jadvali allaqachon mavjud bo'lsa, sxema qayta qo'llanilmaydi
(shu sababli deploy'da xavfsiz qayta ishga tushirish mumkin).

Ishga tushirish (DATABASE_URL muhit o'zgaruvchisida sozlangan bo'lishi shart):
    python -m scripts.init_production_db
"""

import asyncio
from pathlib import Path

import asyncpg

from app.core.config import get_settings


async def apply_schema() -> bool:
    settings = get_settings()
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn)
    try:
        existing = await conn.fetchval("SELECT to_regclass('public.users')")
        if existing:
            print("Sxema allaqachon mavjud — bosqich o'tkazib yuborildi.")
            return False
        schema_sql = (Path(__file__).parent.parent / "db" / "schema.sql").read_text(encoding="utf-8")
        await conn.execute(schema_sql)
        print("Sxema muvaffaqiyatli yaratildi (jadvallar, enumlar, FK, indekslar).")
        return True
    finally:
        await conn.close()


async def apply_migrations() -> None:
    """db/migrations/*.sql — tartib bo'yicha, har ishga tushishda. Har bir fayl
    idempotent yozilgan (IF NOT EXISTS / NOT EXISTS), shuning uchun mavjud
    production bazaga ham, yangi bazaga ham xavfsiz qo'llanadi."""
    settings = get_settings()
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn)
    try:
        for path in sorted((Path(__file__).parent.parent / "db" / "migrations").glob("*.sql")):
            await conn.execute(path.read_text(encoding="utf-8"))
            print(f"Migratsiya qo'llandi: {path.name}")
    finally:
        await conn.close()


async def main() -> None:
    await apply_schema()
    from scripts.seed import seed
    from scripts.seed_geography import seed_geography

    await seed()
    # Seed'dan keyin: 002 migratsiya demo mijozga ham profil yaratishi uchun.
    await apply_migrations()
    await seed_geography()


if __name__ == "__main__":
    asyncio.run(main())
