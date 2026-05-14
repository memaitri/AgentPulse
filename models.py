from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="stopped")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StatusLog(Base):
    __tablename__ = "status_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False)
    old_status = Column(String(20))
    new_status = Column(String(20), nullable=False)
    note = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
