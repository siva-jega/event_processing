from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Kafka configuration
    KAFKA_TOPIC: str = "events"
    KAFKA_SERVER: str = "kafka:9092"

    # OpenTelemetry configuration
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4318"

    # Prometheus configuration
    METRICS_PORT: int = 8005

    # Service configuration
    SERVICE_NAME: str = "ingestion-service"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

from .queue.config import init_kafka_producer

__all__ = ["Settings", "get_settings", "init_kafka_producer"]