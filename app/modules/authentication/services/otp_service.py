import pyotp


def generate_secret() -> str:
    return pyotp.random_base32()


def build_key_uri(email: str, secret: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="ShahPremium")


def verify(token: str, secret: str) -> bool:
    try:
        return pyotp.totp.TOTP(secret).verify(token)
    except Exception:
        return False
