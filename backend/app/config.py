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
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    class Config:
        env_file = ".env"


settings = Settings()
