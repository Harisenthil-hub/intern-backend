"""
Application configuration settings.
All sensitive values are loaded from environment variables (.env file).
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "GasTrack Pro API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── Database ──────────────────────────────────────────────────
    DATABASE_URL: str

    # ── CORS ──────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_value(cls, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return True
        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "on", "dev", "debug"}:
            return True
        if text in {"0", "false", "no", "off", "prod", "production", "release"}:
            return False
        return True


settings = Settings()
