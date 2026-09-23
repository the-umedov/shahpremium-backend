"""Vaqt yordamchisi.

MUHIM: haqiqiy baza ustunlari `timestamp(3) without time zone` (Prisma
`DateTime`ning standart xatti-harakati) — shuning uchun bazaga yoziladigan
yoki undan o'qilgan qiymatlar bilan solishtiriladigan HAR QANDAY "hozir"
qiymati timezone-NAIVE (UTC, lekin tzinfo=None) bo'lishi kerak. asyncpg
timezone-aware datetime'ni naive ustunga bog'lashga urinilsa xato beradi.

API javoblarida ko'rsatiladigan (bazaga yozilmaydigan) timestamp'lar uchun
`datetime.now(timezone.utc)` ishlatishda davom etish mumkin (masalan
health-check javobi) — faqat DB bilan ishlaydigan kodda shu `utcnow()`
funksiyasidan foydalaning.
"""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Timezone-naive UTC 'hozir' — DB ustunlari bilan mos."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
