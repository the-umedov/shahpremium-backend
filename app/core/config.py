import os
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    node_env: str = "development"
    # Render/Railway kabi PaaS'lar portni `$PORT` orqali beradi — u bo'lsa ustunlik
    # qiladi (API_PORT faqat lokal ishlab chiqish uchun).
    api_port: int = int(os.environ.get("PORT", os.environ.get("API_PORT", "4000")))
    api_prefix: str = "/api/v1"
    cors_origin: str = "http://localhost:3000"

    database_url: str
    redis_url: str = "redis://localhost:6379"

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, v: str) -> str:
        """Render/Heroku kabi provayderlar oddiy `postgresql://` (yoki `postgres://`)
        beradi — asyncpg drayveri uchun `postgresql+asyncpg://` ga aylantiramiz."""
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://") :]
        if v.startswith("postgresql://"):
            v = "postgresql+asyncpg://" + v[len("postgresql://") :]
        return v

    jwt_access_secret: str
    jwt_access_ttl: int = 900
    jwt_refresh_secret: str
    jwt_refresh_ttl: int = 1209600

    storage_endpoint: str | None = None
    storage_region: str = "us-east-1"
    storage_bucket: str | None = None
    storage_access_key: str | None = None
    storage_secret_key: str | None = None
    storage_signed_url_ttl: int = 300

    @property
    def is_production(self) -> bool:
        return self.node_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
