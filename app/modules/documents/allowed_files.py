"""documents/allowed-files.js ekvivalenti — ruxsat etilgan hujjat formatlari va cheklovlar."""

from __future__ import annotations

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

ALLOWED_MIME: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


def is_allowed_mime(mime: str | None) -> bool:
    return mime in ALLOWED_MIME


def ext_for_mime(mime: str | None) -> str:
    return ALLOWED_MIME.get(mime or "", "")


def mime_for_ext(ext: str) -> str:
    for mime, e in ALLOWED_MIME.items():
        if e == ext:
            return mime
    return "application/octet-stream"
