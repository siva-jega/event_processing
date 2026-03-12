import psycopg2
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus
from contextlib import contextmanager

logger = logging.getLogger("consumer")


class PostgresSettings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "events_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_postgres_settings() -> PostgresSettings:
    return PostgresSettings()

def get_database_settings():
    """Return Postgres settings.

    This provides access to the Postgres settings for this service.
    """
    return get_postgres_settings()


def init_db():
    """Initialize and return a PostgreSQL connection using shared settings.

    Returns:
        psycopg2.connection: Database connection
    """
    pg = get_postgres_settings()
    dsn = f"postgresql://{pg.POSTGRES_USER}:{quote_plus(pg.POSTGRES_PASSWORD)}@{pg.POSTGRES_HOST}:{pg.POSTGRES_PORT}/{pg.POSTGRES_DB}"

    conn = psycopg2.connect(dsn)
    logger.info("database connection established")
    return conn

@contextmanager
def get_conn():
    """Context manager that yields a fresh DB connection and ensures it is closed.

    This keeps the lifecycle local to callers and supports dependency injection
    by passing this factory around. Creating/closing a connection per use is
    intentional here to simplify resource ownership and make behavior explicit.
    """
    conn = None
    try:
        conn = init_db()
        yield conn
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def ensure_table(conn):
    """Ensure the events table exists in the database.

    Args:
        conn: psycopg2 database connection
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_name TEXT NOT NULL,
                metadata JSONB,
                timestamp TIMESTAMP WITH TIME ZONE,
                processed_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
            """
        )
        conn.commit()
    logger.info("events table verified")
