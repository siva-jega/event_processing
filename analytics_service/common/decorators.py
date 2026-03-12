import functools
from typing import Optional


def with_cursor(cursor_factory: Optional[object] = None):
    """Decorator to provide a DB cursor to repository methods.

    Behavior:
    - If the repository instance already has a bound connection on
      ``self._conn``, use that connection and create/close a cursor from it.
    - Otherwise, obtain a connection from the pool via
      ``config.database.get_connection()`` and create/close a cursor.

    The cursor is made available to the method as ``self._cur``. Methods
    should use ``self._cur.execute(...)``, ``self._cur.fetchall()`` etc.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            from config.database import get_connection

            conn = getattr(self, "_conn", None)

            def _use_cursor(conn_obj):
                if cursor_factory:
                    cur = conn_obj.cursor(cursor_factory=cursor_factory)
                else:
                    cur = conn_obj.cursor()
                try:
                    setattr(self, "_cur", cur)
                    return func(self, *args, **kwargs)
                finally:
                    try:
                        cur.close()
                    except Exception:
                        pass
                    if hasattr(self, "_cur"):
                        delattr(self, "_cur")

            if conn is None:
                with get_connection() as pooled_conn:
                    return _use_cursor(pooled_conn)
            else:
                return _use_cursor(conn)

        return wrapper

    return decorator
