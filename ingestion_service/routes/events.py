from fastapi import APIRouter, HTTPException, status
import json
import logging
import hashlib
import asyncio
from prometheus_client import Counter

from dto import Event, EventResponse
from config.config import get_settings
from services import kafka_service

router = APIRouter()
settings = get_settings()
logger = logging.getLogger("ingestion")

events_ingested = Counter("events_ingested_total", "Total events accepted by ingestion service")


@router.post("/events", status_code=status.HTTP_202_ACCEPTED, response_model=EventResponse)
async def post_event(event: Event):
    """Accept an event, validate, and publish to Kafka.

    Uses aiokafka for higher throughput and OpenTelemetry tracing.
    """
    try:
        payload = {
            "user_id": str(event.user_id),
            "event_name": event.event_name,
            "metadata": event.metadata,
            "timestamp": event.timestamp.isoformat()
        }

        digest = hashlib.sha256((payload["user_id"] + payload["event_name"] + payload["timestamp"]).encode()).hexdigest()

        asyncio.create_task(kafka_service.send_event_to_kafka(payload))
        events_ingested.inc()
        logger.info("event_received user=%s event=%s id=%s", payload["user_id"], payload["event_name"], digest)
        return EventResponse(status="accepted", event_id=digest)
    except Exception as e:
        logger.exception("failed to publish event")
        raise HTTPException(status_code=500, detail=str(e))
