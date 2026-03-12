from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_TOPIC: str = "events"
    KAFKA_SERVER: str = "kafka:9092"
    KAFKA_GROUP: str = "event_consumer_group"

    METRICS_PORT: int = 8003

    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4318"

    BATCH_SIZE: int = 500  
    BATCH_TIMEOUT: float = 0.5  

    MAX_CONNECTIONS: int = 20
    CONNECTION_TIMEOUT: float = 30.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

from .queue.config import create_consumer, create_dlq_producer
from .database.config import get_database_settings, init_db, ensure_table, get_conn
from .tracing.config import init_tracer


__all__ = [
    "Settings",
    "get_settings",
    "create_consumer",
    "create_dlq_producer",
    "init_tracer",
    "get_database_settings",
    "init_db",
    "get_conn",
    "ensure_table",
]
