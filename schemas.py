from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Auth
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Agent
class AgentCreate(BaseModel):
    name: str
    type: str
    status: Optional[str] = "stopped"

class AgentStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None

class AgentResponse(BaseModel):
    id: int
    name: str
    type: str
    status: str
    created_at: datetime
    health_summary: Optional[str] = None

    class Config:
        from_attributes = True

# Status Log
class StatusLogResponse(BaseModel):
    id: int
    agent_id: int
    old_status: Optional[str]
    new_status: str
    note: Optional[str]
    changed_at: datetime

    class Config:
        from_attributes = True
