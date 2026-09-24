"""O'zbekistonning 14 ta hududi (12 viloyat, Qoraqalpog'iston Respublikasi,
Toshkent shahri) va ularning tumanlarini bazaga qo'shadi.

Idempotent: mavjud viloyat nomi yoki ISO kodi bo'yicha topiladi (takror
yaratilmaydi), faqat yetishmayotgan tumanlar qo'shiladi. Foydalanuvchi o'zi
qo'shgan viloyat/tumanlarga tegmaydi.

    python -m scripts.seed_geography
"""

from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import SessionLocal
from app.models.models import District, Region

# (ISO 3166-2 kodi, rasmiy nomi, eski/qisqa nomlar, tumanlar)
REGIONS: list[tuple[str, str, list[str], list[str]]] = [
    ("UZ-TK", "Toshkent shahri", ["toshkent", "toshkent sh", "tashkent"], [
        "Bektemir", "Chilonzor", "Mirobod", "Mirzo Ulug'bek", "Olmazor", "Sergeli",
        "Shayxontohur", "Uchtepa", "Yakkasaroy", "Yangihayot", "Yashnobod", "Yunusobod",
    ]),
    ("UZ-QR", "Qoraqalpog'iston Respublikasi", ["qoraqalpogiston"], [
        "Amudaryo", "Beruniy", "Bo'zatov", "Chimboy", "Ellikqal'a", "Kegeyli", "Mo'ynoq", "Nukus",
        "Qanliko'l", "Qo'ng'irot", "Qorao'zak", "Shumanay", "Taxiatosh", "Taxtako'pir", "To'rtko'l",
        "Xo'jayli",
    ]),
    ("UZ-AN", "Andijon viloyati", ["andijon"], [
        "Andijon", "Asaka", "Baliqchi", "Bo'ston", "Buloqboshi", "Izboskan", "Jalaquduq",
        "Marhamat", "Oltinko'l", "Paxtaobod", "Qo'rg'ontepa", "Shahrixon", "Ulug'nor", "Xo'jaobod",
    ]),
    ("UZ-BU", "Buxoro viloyati", ["buxoro"], [
        "Buxoro", "G'ijduvon", "Jondor", "Kogon", "Olot", "Peshku", "Qorako'l", "Qorovulbozor",
        "Romitan", "Shofirkon", "Vobkent",
    ]),
    ("UZ-FA", "Farg'ona viloyati", ["fargona"], [
        "Bag'dod", "Beshariq", "Buvayda", "Dang'ara", "Farg'ona", "Furqat", "Oltiariq", "O'zbekiston",
        "Qo'shtepa", "Quva", "Rishton", "So'x", "Toshloq", "Uchko'prik", "Yozyovon",
    ]),
    ("UZ-JI", "Jizzax viloyati", ["jizzax"], [
        "Arnasoy", "Baxmal", "Do'stlik", "Forish", "G'allaorol", "Mirzacho'l", "Paxtakor",
        "Sharof Rashidov", "Yangiobod", "Zafarobod", "Zarbdor", "Zomin",
    ]),
    ("UZ-NG", "Namangan viloyati", ["namangan"], [
        "Chortoq", "Chust", "Kosonsoy", "Mingbuloq", "Namangan", "Norin", "Pop", "To'raqo'rg'on",
        "Uchqo'rg'on", "Uychi", "Yangiqo'rg'on",
    ]),
    ("UZ-NW", "Navoiy viloyati", ["navoiy"], [
        "Karmana", "Konimex", "Navbahor", "Nurota", "Qiziltepa", "Tomdi", "Uchquduq", "Xatirchi",
    ]),
    ("UZ-QA", "Qashqadaryo viloyati", ["qashqadaryo"], [
        "Chiroqchi", "Dehqonobod", "G'uzor", "Kasbi", "Kitob", "Koson", "Ko'kdala", "Mirishkor",
        "Muborak", "Nishon", "Qamashi", "Qarshi", "Shahrisabz", "Yakkabog'",
    ]),
    ("UZ-SA", "Samarqand viloyati", ["samarqand"], [
        "Bulung'ur", "Ishtixon", "Jomboy", "Kattaqo'rg'on", "Narpay", "Nurobod", "Oqdaryo",
        "Pastdarg'om", "Paxtachi", "Payariq", "Qo'shrabot", "Samarqand", "Toyloq", "Urgut",
    ]),
    ("UZ-SI", "Sirdaryo viloyati", ["sirdaryo"], [
        "Boyovut", "Guliston", "Mirzaobod", "Oqoltin", "Sardoba", "Sayxunobod", "Sirdaryo", "Xovos",
    ]),
    ("UZ-SU", "Surxondaryo viloyati", ["surxondaryo"], [
        "Angor", "Bandixon", "Boysun", "Denov", "Jarqo'rg'on", "Muzrabot", "Oltinsoy", "Qiziriq",
        "Qumqo'rg'on", "Sariosiyo", "Sherobod", "Sho'rchi", "Termiz", "Uzun",
    ]),
    ("UZ-TO", "Toshkent viloyati", ["toshkent vil", "toshkent viloyati"], [
        "Bekobod", "Bo'ka", "Bo'stonliq", "Chinoz", "Ohangaron", "Oqqo'rg'on", "O'rta Chirchiq",
        "Parkent", "Piskent", "Qibray", "Quyi Chirchiq", "Toshkent", "Yangiyo'l", "Yuqori Chirchiq",
        "Zangiota",
    ]),
    ("UZ-XO", "Xorazm viloyati", ["xorazm"], [
        "Bog'ot", "Gurlan", "Hazorasp", "Qo'shko'pir", "Shovot", "Tuproqqal'a", "Urganch", "Xiva",
        "Xonqa", "Yangiariq", "Yangibozor",
    ]),
]


def _norm(name: str) -> str:
    s = name.lower().strip()
    for ch in "'`ʻʼ‘’":
        s = s.replace(ch, "")
    return " ".join(s.split())


def _match(existing: list[Region], code: str, name: str, aliases: list[str]) -> Region | None:
    wanted = {_norm(name), *(_norm(a) for a in aliases)}
    for region in existing:
        if region.code.upper() == code or _norm(region.name) in wanted:
            return region
    return None


async def seed_geography() -> None:
    async with SessionLocal() as db:
        existing = list(
            (await db.execute(select(Region).options(selectinload(Region.districts)))).scalars().all()
        )
        used_codes = {r.code.upper() for r in existing}
        created_regions = created_districts = 0

        for code, name, aliases, districts in REGIONS:
            region = _match(existing, code, name, aliases)
            if region is None:
                region = Region(code=code if code not in used_codes else f"{code}-1", name=name, districts=[])
                db.add(region)
                existing.append(region)
                created_regions += 1
            else:
                region.name = name  # qisqa nom ("Buxoro") -> rasmiy nom ("Buxoro viloyati")

            have = {_norm(d.name) for d in region.districts}
            for district in districts:
                full = f"{district} tumani"
                if _norm(full) not in have:
                    region.districts.append(District(name=full))
                    have.add(_norm(full))
                    created_districts += 1

        await db.commit()
        print(f"Geografiya: {created_regions} ta viloyat va {created_districts} ta tuman qo'shildi.")


if __name__ == "__main__":
    asyncio.run(seed_geography())
