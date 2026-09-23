import logging
import re

_REDACT_KEYS = {"password", "newpassword", "currentpassword", "token", "otp", "authorization", "cookie"}
_REDACT_PATTERN = re.compile(r'("(?:' + "|".join(_REDACT_KEYS) + r')"\s*:\s*)"[^"]*"', re.IGNORECASE)


class RedactingFilter(logging.Filter):
    """parol/token/cookie hech qachon logga tushmasin."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _REDACT_PATTERN.sub(r'\1"[REDACTED]"', record.msg)
        return True


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(RedactingFilter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], format="%(asctime)s %(levelname)s %(name)s %(message)s")
