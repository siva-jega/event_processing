from pydantic import BaseModel


class EventResponse(BaseModel):
    """Response model for event ingestion."""
    status: str
    event_id: str