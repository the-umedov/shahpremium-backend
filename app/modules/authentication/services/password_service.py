from app.core.security import hash_password, verify_password

DUMMY_HASH = (
    "$argon2id$v=19$m=19456,t=2,p=1$c2FsdHNhbHRzYWx0$"
    "0000000000000000000000000000000000000000000"
)


async def hash(plain: str) -> str:
    return hash_password(plain)


async def verify(hashed: str, plain: str) -> bool:
    return verify_password(hashed, plain)
