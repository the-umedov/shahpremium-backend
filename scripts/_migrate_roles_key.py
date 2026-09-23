"""Bir martalik migratsiya: `roles.key` ustunini native Postgres ENUM'dan
oddiy `text`'ga o'tkazadi — SUPER_ADMIN UI orqali erkin (arbitrar) yangi rol
yaratishi mumkin bo'lishi uchun (ENUM cheklovi buni bloklaydi)."""

import asyncio

from app.core.database import engine
from sqlalchemy import text


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE roles ALTER COLUMN key TYPE text;"))
    print("OK: roles.key endi text turida")


if __name__ == "__main__":
    asyncio.run(main())
