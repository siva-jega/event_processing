from datetime import datetime
from pydantic import BaseModel, Field


class Event(BaseModel):
    """Data Transfer Object for incoming events.
    
    Attributes:
        user_id (str): Unique identifier for the user
        event_name (str): Name of the event
        metadata (dict): Additional event data
        timestamp (datetime): When the event occurred
    """
    user_id: str = Field(..., alias="user_id")
    event_name: str = Field(..., alias="event_name")
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime