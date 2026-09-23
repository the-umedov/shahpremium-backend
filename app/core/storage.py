from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

from app.core.config import get_settings

settings = get_settings()


class StorageService:
    """Lokal disk fayl xotira — fayllar PUBLIC katalogdan TASHQARIDA saqlanadi.

    Kirish faqat HMAC bilan imzolangan, muddati cheklangan havola orqali.
    Prod'da bu S3/MinIO adapteri bilan almashtiriladi (interfeys bir xil).
    """

    def __init__(self) -> None:
        self.root = Path.cwd() / ".storage"
        self.secret = settings.jwt_access_secret or "storage-secret"
        self.ttl = settings.storage_signed_url_ttl or 300

    def save(self, data: bytes, mime_type: str, ext: str = "") -> dict:
        key = f"{time.gmtime().tm_year}/{uuid.uuid4()}{ext}"
        full = self.root / key
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(data)
        return {
            "storage_key": key,
            "size_bytes": len(data),
            "checksum": hashlib.sha256(data).hexdigest(),
            "mime_type": mime_type,
        }

    def read(self, storage_key: str) -> bytes:
        return (self.root / self._safe_key(storage_key)).read_bytes()

    def remove(self, storage_key: str) -> None:
        (self.root / self._safe_key(storage_key)).unlink(missing_ok=True)

    def sign(self, key: str, exp: int) -> str:
        return hmac.new(self.secret.encode(), f"{key}.{exp}".encode(), hashlib.sha256).hexdigest()

    def create_signed_path(self, storage_key: str) -> str:
        exp = int(time.time()) + self.ttl
        sig = self.sign(storage_key, exp)
        query = urlencode({"key": storage_key, "exp": exp, "sig": sig})
        return f"/documents/download?{query}"

    def verify_signature(self, key: str, exp: int, sig: str) -> bool:
        if exp < int(time.time()):
            return False
        expected = self.sign(key, exp)
        return hmac.compare_digest(expected, sig)

    @staticmethod
    def _safe_key(key: str) -> str:
        clean = key.replace("\\", "/")
        if ".." in clean:
            raise ValueError("Noto'g'ri storage key")
        return clean


storage_service = StorageService()
