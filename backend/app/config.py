from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

BACKEND_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "ParentBridge"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase PostgreSQL connection
    DATABASE_URL: str = "postgresql+asyncpg://postgres:your-supabase-password@db.your-project.supabase.co:5432/postgres"

    # JWT Authentication
    JWT_SECRET_KEY: str = "supersecret_parentbridge_jwt_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3  # 3 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        extra="ignore"
    )


settings = Settings()
