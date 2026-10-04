from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
        case_sensitive=False,
    )
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    app_env: str = "production"
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "postgres"
    postgres_port: int = Field(default=5432, ge=1, le=65535)
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator(
        "postgres_db", "postgres_user", "postgres_host", "postgres_password"
    )
    @classmethod
    def required_value(cls, value: str) -> str:
        if not value or value.startswith("replace-with"):
            raise ValueError("Set a real database configuration value")
        return value

    @model_validator(mode="after")
    def production_configuration(self):
        if self.jwt_secret_key.startswith("replace-with"):
            raise ValueError("Set a random JWT_SECRET_KEY of at least 32 characters")
        if (
            self.app_env != "development"
            and self.postgres_password == "local-development-only"
        ):
            raise ValueError("Production requires a non-development database password")
        if "*" in self.allowed_origins:
            raise ValueError(
                "CORS_ORIGINS must contain explicit origins, not a wildcard"
            )
        return self

    @property
    def database_url(self) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
