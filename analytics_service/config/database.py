"""Database helper moved from repo to config.

Provides a single helper to obtain a psycopg2 connection using the
application settings. Kept here so configuration-related helpers live under
the `config` package.
"""

from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Optional
from config.config import get_settings

settings = get_settings()

# Connection pool instance (module scoped)
_pool: Optional[SimpleConnectionPool] = None


def init_pool(minconn: int = 1, maxconn: int = 10):
    """Initialize a SimpleConnectionPool for psycopg2 connections.

    This should be called once at application startup.
    """
    global _pool
    if _pool is None:
        dsn = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        _pool = SimpleConnectionPool(minconn, maxconn, dsn=dsn)


def close_pool():
    """Close all connections in the pool. Call at application shutdown."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_connection():
    """Context manager that yields a connection from the pool.

    If the pool hasn't been initialized yet, it will be created with default
    min/max sizes.
    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(...)
    """
    global _pool
    if _pool is None:
        init_pool()
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)


__all__ = ["init_pool", "close_pool", "get_connection"]