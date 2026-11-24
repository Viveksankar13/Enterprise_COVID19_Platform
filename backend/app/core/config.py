import os
from typing import Any, List, Union
from pydantic import AnyHttpUrl, BeforeValidator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


def parse_cors_origins(v: Any) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application Settings ──
    APP_NAME: str = "Enterprise COVID-19 Analytics Platform"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "DEVELOPMENT_SECRET_KEY_PLACEHOLDER_CHANGE_ME_IN_PRODUCTION_MIN_64_CHARS"

    # ── PostgreSQL Database Settings ──
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "covid19_analytics"
    POSTGRES_USER: str = "covid_admin"
    POSTGRES_PASSWORD: str = "change_me_strong_password"
    POSTGRES_SCHEMA: str = "public"
    DATABASE_URL: str = ""

    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """
        Dynamically constructs the async pg database URL.
        Converts postgresql:// to postgresql+asyncpg:// if needed.
        """
        url = self.DATABASE_URL
        if not url:
            url = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """
        Constructs sync URL for Alembic or scripts using psycopg2.
        """
        url = self.DATABASE_URL
        if not url:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)
        return url

    # ── JWT Authentication Settings ──
    JWT_SECRET_KEY: str = "DEVELOPMENT_JWT_SECRET_KEY_PLACEHOLDER_CHANGE_ME_MIN_32_CHARS"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS Settings ──
    ALLOWED_ORIGINS: Annotated[
        List[str], BeforeValidator(parse_cors_origins)
    ] = ["http://localhost:3000", "http://localhost:5173"]

    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # ── Power BI Embedded Settings ──
    POWERBI_TENANT_ID: str = ""
    POWERBI_CLIENT_ID: str = ""
    POWERBI_CLIENT_SECRET: str = ""
    POWERBI_WORKSPACE_ID: str = ""
    POWERBI_REPORT_ID: str = ""

    # ── Redis Settings ──
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    @property
    def REDIS_URL(self) -> str:
        password_str = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_str}{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # ── ETL Configuration ──
    OWID_DATASET_URL: str = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    OWID_DATASET_CODEBOOK_URL: str = "https://covid.ourworldindata.org/data/owid-covid-codebook.csv"
    ETL_DATA_DIR: str = "/app/data"
    ETL_RAW_DIR: str = "/app/data/raw"
    ETL_PROCESSED_DIR: str = "/app/data/processed"
    ETL_ARCHIVE_DIR: str = "/app/data/archive"
    ETL_LOGS_DIR: str = "/app/logs/etl"


settings = Settings()
