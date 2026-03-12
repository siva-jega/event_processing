import json
import logging
import asyncio
from typing import Callable, Iterable, List, Optional, Tuple, ContextManager, cast
from models import Event
from repo.events import insert_events
from prometheus_client import Counter

logger = logging.getLogger("consumer")

events_processed = Counter("events_processed_total", "Total events processed and stored")


Row = Tuple[str, str, str, str, str]


async def _parse_record(r) -> Optional[Row]:
    """Parse a single Kafka record into a DB row tuple or return None on failure."""
    try:
        value = r.value.decode() if isinstance(r.value, (bytes, bytearray)) else r.value
        payload = json.loads(value) if isinstance(value, str) else value
        ev = Event(**payload)
        return (ev.event_id(), ev.user_id, ev.event_name, json.dumps(ev.metadata), ev.timestamp.isoformat())
    except Exception:
        logger.exception("skip bad record")
        return None


async def process_batch(
    records: Iterable,
    get_conn: Callable[[], ContextManager],
    insert_fn: Callable[[List[Row], Callable[[], ContextManager]], int] = insert_events,
) -> None:
    """Process a batch of Kafka records asynchronously.

    - Parses records concurrently.
    - Delegates DB writes to `insert_fn` executed in a thread (via asyncio.to_thread).
    - Keeps metrics and logging in the orchestration layer.

    Args:
        records: Iterable of Kafka consumer records
        get_conn: contextmanager factory that yields DB connections
        insert_fn: repository insert function (injected for testability)
    """
    records = list(records)
    if not records:
        return

    tasks = [_parse_record(r) for r in records]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    rows = [r for r in results if r is not None and not isinstance(r, Exception)]
    rows_cast = cast(List[Row], rows)

    if not rows:
        return

    try:
        inserted = await asyncio.to_thread(insert_fn, rows_cast, get_conn)
        events_processed.inc(inserted)
        logger.info("inserted %s rows", inserted)
    except Exception:
        logger.exception("failed to insert rows (repo)")
