from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any
import hashlib
import json


class Event(BaseModel):
    user_id: str = Field(...)
    event_name: str = Field(...)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime

    def event_id(self) -> str:
        key = f"{self.user_id}|{self.event_name}|{self.timestamp.isoformat()}|{json.dumps(self.metadata, sort_keys=True)}"
        return hashlib.sha256(key.encode()).hexdigest()