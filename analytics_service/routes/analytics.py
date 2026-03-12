"""Analytics routes."""

from fastapi import APIRouter, HTTPException, Depends
from prometheus_client import Counter
import json
from math import ceil

from config.config import get_settings
from services import (
    get_cache,
    set_cache,
)
from services import EventsRepo, get_events_repo

router = APIRouter(tags=["analytics"])
settings = get_settings()

queries_count = Counter("analytics_queries_total", "Total analytics queries")


@router.get("/events/count")
def events_count(from_ts: str, to_ts: str, repo: EventsRepo = Depends(get_events_repo)):
    """Get total event count within a time range."""
    queries_count.inc()
    try:
        count = repo.get_event_count(from_ts, to_ts)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-events")
async def top_events(limit: int = 5, repo: EventsRepo = Depends(get_events_repo)):
    """Get top events by frequency."""
    queries_count.inc()
    cache_key = f"top_events:{limit}"
    try:
        cached = await get_cache(cache_key)
        if cached:
            return {"top_events": json.loads(cached), "cached": True}

        result = repo.get_top_events(limit)
        await set_cache(cache_key, result, 30)
        return {"top_events": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/active")
async def active_users(
    window: str = "24h", repo: EventsRepo = Depends(get_events_repo)
):
    """Get count of active users within the specified window."""
    queries_count.inc()
    try:
        if window.endswith("h"):
            hours = int(window[:-1])
        elif window.endswith("m"):
            minutes = int(window[:-1])
            hours = ceil(minutes / 60)
        else:
            hours = 24

        cache_key = f"active_users:{window}"
        cached = await get_cache(cache_key)
        if cached:
            return {"active_users": int(cached), "window": window, "cached": True}

        count = repo.get_active_users(hours)
        await set_cache(cache_key, count, 60)
        return {"active_users": count, "window": window}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/events")
async def user_events(
    user_id: str, limit: int = 10, repo: EventsRepo = Depends(get_events_repo)
):
    """Get recent events for a specific user."""
    queries_count.inc()
    cache_key = f"user_events:{user_id}:{limit}"
    try:
        cached = await get_cache(cache_key)
        if cached:
            return {"user_id": user_id, "events": json.loads(cached), "cached": True}

        events = repo.get_user_events(user_id, limit)
        await set_cache(cache_key, events, 60)
        return {"user_id": user_id, "events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
