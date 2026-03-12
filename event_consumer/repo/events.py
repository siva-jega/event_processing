import logging
from opentelemetry import trace
from psycopg2.extras import execute_values

logger = logging.getLogger("consumer")


def insert_events(rows, get_conn):
    """Insert rows into the events table using the provided connection factory.

    Args:
        rows: list of row tuples to insert
        get_conn: a contextmanager that yields a DB connection (e.g., from config.get_conn)

    Returns:
        int: number of rows attempted to insert (len(rows))
    """
    if not rows:
        return 0

    tracer = trace.get_tracer("event-consumer.repo")
    sql = (
        "INSERT INTO events (event_id, user_id, event_name, metadata, timestamp)"
        " VALUES %s ON CONFLICT (event_id) DO NOTHING"
    )

    with get_conn() as conn:
        try:
            with conn.cursor() as cur:
                with tracer.start_as_current_span("db.insert_events"):
                    execute_values(cur, sql, rows)
            conn.commit()
        except Exception:
            logger.exception("failed to insert rows in repo")
            try:
                conn.rollback()
            except Exception:
                pass
            raise

    return len(rows)
