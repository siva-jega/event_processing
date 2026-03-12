"""Database service for analytics operations.

Provides an EventsRepo class that encapsulates operations using a single
connection. Module-level helper functions remain for backward compatibility
and will obtain a pooled connection internally.
"""

import psycopg2.extras
from typing import List, Dict, Any
from common.decorators import with_cursor


class EventsRepo:
    """Repository object bound to a single DB connection.

    Use this when you already have a connection (for example via a
    dependency or a transaction). The instance methods do not require a
    `conn` parameter.
    """

    def __init__(self, conn):
        self._conn = conn
        from typing import Any

        self._cur: Any = None

    @with_cursor()
    def get_event_count(self, from_ts: str, to_ts: str) -> int:
        self._cur.execute(
            "SELECT COUNT(*) FROM events WHERE timestamp >= %s AND timestamp <= %s",
            (from_ts, to_ts),
        )
        row = self._cur.fetchone()
        return row[0]

    @with_cursor(cursor_factory=psycopg2.extras.DictCursor)
    def get_top_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        self._cur.execute(
            "SELECT event_name, COUNT(*) AS cnt FROM events GROUP BY event_name ORDER BY cnt DESC LIMIT %s",
            (limit,),
        )
        rows = self._cur.fetchall()
        return [{"event_name": r[0], "count": r[1]} for r in rows]

    def get_active_users(self, window_hours: int = 24) -> int:
        from datetime import datetime, timedelta

        since = datetime.utcnow() - timedelta(hours=window_hours)

        @with_cursor()
        def _inner(self):
            self._cur.execute(
                "SELECT COUNT(DISTINCT user_id) FROM events WHERE timestamp >= %s",
                (since.isoformat(),),
            )
            row = self._cur.fetchone()
            return row[0]

        return _inner(self)

    @with_cursor(cursor_factory=psycopg2.extras.DictCursor)
    def get_user_events(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        self._cur.execute(
            "SELECT event_name, metadata, timestamp FROM events WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s",
            (user_id, limit),
        )
        rows = self._cur.fetchall()
        return [
            {"event_name": r[0], "metadata": r[1], "timestamp": r[2].isoformat()}
            for r in rows
        ]


__all__ = [
    "EventsRepo",
]
