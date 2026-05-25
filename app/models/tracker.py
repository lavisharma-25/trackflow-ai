from pydantic import BaseModel
from typing import Dict, Any, Optional


class TrackerCreateRequest(BaseModel):
    tracker_name: str
    schema: Dict[str, str]


class AgentRequest(BaseModel):
    query: str


class ParsedCommand(BaseModel):
    intent: str
    tracker: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None