from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from database import engine, get_db, Base
from models import Agent, StatusLog
from schemas import (
    AgentCreate, AgentStatusUpdate, AgentResponse,
    StatusLogResponse, TokenResponse
)
from auth import verify_token, create_access_token, authenticate_user
from llm import generate_health_summary

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgentPulse",
    description="AI Agent Monitoring API — Hapticware Hackathon",
    version="1.0.0"
)

# Serve static dashboard
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(username: str, password: str):
    """Get a JWT token. Use username: admin, password: password123"""
    if not authenticate_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token(data={"sub": username})
    return {"access_token": token}


# ─────────────────────────────────────────────
# AGENTS
# ─────────────────────────────────────────────

@app.post("/agents", response_model=AgentResponse, status_code=201, tags=["Agents"])
def register_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Register a new AI agent."""
    existing = db.query(Agent).filter(Agent.name == agent.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Agent '{agent.name}' already exists")

    valid_statuses = ["running", "stopped", "error", "idle"]
    if agent.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")

    new_agent = Agent(name=agent.name, type=agent.type, status=agent.status)
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    # Log initial status
    log = StatusLog(agent_id=new_agent.id, old_status=None, new_status=agent.status, note="Agent registered")
    db.add(log)
    db.commit()

    return new_agent


@app.patch("/agents/{agent_id}/status", response_model=AgentResponse, tags=["Agents"])
def update_agent_status(
    agent_id: int,
    update: AgentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Update an agent's status (running / stopped / error / idle)."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    valid_statuses = ["running", "stopped", "error", "idle"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")

    old_status = agent.status
    agent.status = update.status
    db.commit()
    db.refresh(agent)

    # Log the change
    log = StatusLog(agent_id=agent.id, old_status=old_status, new_status=update.status, note=update.note)
    db.add(log)
    db.commit()

    return agent


@app.get("/agents", response_model=List[AgentResponse], tags=["Agents"])
async def get_all_agents(
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Get all agents with their current state and AI-generated health summary."""
    agents = db.query(Agent).all()
    result = []

    for agent in agents:
        logs = db.query(StatusLog).filter(StatusLog.agent_id == agent.id).all()
        log_statuses = [log.new_status for log in logs]

        summary = await generate_health_summary(agent.name, agent.type, agent.status, log_statuses)

        agent_dict = {
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "status": agent.status,
            "created_at": agent.created_at,
            "health_summary": summary
        }
        result.append(agent_dict)

    return result


@app.get("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Get a single agent by ID with health summary."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    logs = db.query(StatusLog).filter(StatusLog.agent_id == agent.id).all()
    log_statuses = [log.new_status for log in logs]
    summary = await generate_health_summary(agent.name, agent.type, agent.status, log_statuses)

    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.type,
        "status": agent.status,
        "created_at": agent.created_at,
        "health_summary": summary
    }


@app.delete("/agents/{agent_id}", tags=["Agents"])
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Delete an agent and its logs."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.query(StatusLog).filter(StatusLog.agent_id == agent_id).delete()
    db.delete(agent)
    db.commit()
    return {"message": f"Agent '{agent.name}' deleted successfully"}


# ─────────────────────────────────────────────
# LOGS
# ─────────────────────────────────────────────

@app.get("/agents/{agent_id}/logs", response_model=List[StatusLogResponse], tags=["Logs"])
def get_agent_logs(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Get full status history for an agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    logs = db.query(StatusLog).filter(StatusLog.agent_id == agent_id).all()
    return logs


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serve the visual dashboard."""
    return FileResponse(os.path.join(BASE_DIR, "static", "dashboard.html"))


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "AgentPulse"}
