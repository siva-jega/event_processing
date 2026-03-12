"""Service DI wrapper for EventsRepo.

This module exposes a `get_events_repo` FastAPI dependency that yields an
`EventsRepo` instance bound to a pooled connection. This keeps DI at the
`services` layer while keeping repository code in `repo.events`.
"""

from contextlib import contextmanager
from typing import Generator

from config.database import get_connection
from repo.events import EventsRepo


@contextmanager
def _repo_scope() -> Generator[EventsRepo, None, None]:
    with get_connection() as conn:
        yield EventsRepo(conn)


def get_events_repo() -> Generator[EventsRepo, None, None]:
    """FastAPI dependency that yields an EventsRepo for the request."""
    with _repo_scope() as repo:
        yield repo


__all__ = ["EventsRepo", "get_events_repo"]
