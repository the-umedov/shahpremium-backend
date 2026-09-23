"""Bir martalik tekshiruv: ORM haqiqiy bazadagi ustunlarga to'g'ri mos keladimi."""

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import SessionLocal
from app.models.models import Role, User, UserRole


async def main() -> None:
    async with SessionLocal() as db:
        roles = (await db.execute(select(Role).order_by(Role.key))).scalars().all()
        print(f"ROLES ({len(roles)}):")
        for r in roles:
            print(f"  {r.key.value:12s} {r.name!r} is_system={r.is_system}")

        users = (
            await db.execute(
                select(User).options(selectinload(User.roles).selectinload(UserRole.role)).order_by(User.email)
            )
        ).scalars().all()
        print(f"\nUSERS ({len(users)}):")
        for u in users:
            role_keys = [ur.role.key.value for ur in u.roles]
            print(f"  {u.email:35s} type={u.type.value:10s} active={u.is_active} roles={role_keys}")


if __name__ == "__main__":
    asyncio.run(main())
