"""Analytics services package exports.

Re-exports commonly-used service providers so callers can import from
`services` instead of drilling into implementation modules.
"""

from .cache_service import (
    init_redis,
    get_cache,
    set_cache,
    close_redis,
)
from .events import EventsRepo, get_events_repo

__all__ = [
    "init_redis",
    "get_cache",
    "set_cache",
    "close_redis",
    "EventsRepo",
    "get_events_repo",
]
