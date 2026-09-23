from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
async def check() -> dict:
    """Monitoring uchun — public, maxfiy ma'lumot bermaydi."""
    db_status = "down"
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "up"
    except Exception:
        db_status = "down"
    return {
        "status": "ok" if db_status == "up" else "degraded",
        "db": db_status,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
