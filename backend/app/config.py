import json
import secrets
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./retro.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost", "http://localhost:80"]

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # JWT Settings
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Frontend URL for OAuth redirect
    frontend_url: str = "http://localhost:5173"

    # Backend URL for OAuth callback (needed behind reverse proxies)
    backend_url: str = "http://localhost:8000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("database_url", mode="before")
    @classmethod
    def convert_postgres_url(cls, v):
        # Convert postgres:// to postgresql+asyncpg:// for SQLAlchemy async
        if v and v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v and v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg uses 'ssl' instead of 'sslmode'
        if v and "sslmode=" in v:
            v = v.replace("sslmode=", "ssl=")
        # Remove channel_binding parameter (Neon-specific, not supported by asyncpg)
        if v and "channel_binding=" in v:
            import re
            v = re.sub(r"[&?]channel_binding=[^&]*", "", v)
        return v

    class Config:
        env_file = ".env"


settings = Settings()
