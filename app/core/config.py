"""
Application configuration settings.
All sensitive values are loaded from environment variables (.env file).
"""

from pydantic_settings import BaseSettings


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


settings = Settings()
