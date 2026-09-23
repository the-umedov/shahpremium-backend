"""Yangi (bo'sh) Render/production PostgreSQL bazasini bir martalik tayyorlaydi:

1) db/schema.sql'ni qo'llaydi — barcha jadval/enum/FK/indekslarni yaratadi
   (E:\\pgdata-shahpremium dagi asl Prisma bazasidan olingan haqiqiy sxema).
2) scripts/seed.py chaqiriladi — 7 tizim roli, 48 ruxsat, 6 demo foydalanuvchi.

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


async def main() -> None:
    await apply_schema()
    from scripts.seed import seed

    await seed()


if __name__ == "__main__":
    asyncio.run(main())
