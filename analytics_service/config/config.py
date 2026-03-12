"""Analytics service configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "events_db"

    # Redis configuration
    REDIS_URL: str = "redis://redis:6379/0"

    # OpenTelemetry configuration
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4318"

    # Service configuration
    SERVICE_NAME: str = "analytics-service"
    METRICS_PORT: int = 8004

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]