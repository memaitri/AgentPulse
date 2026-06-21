
# AgentPulse — Mini Agent Monitor API
<img width="1912" height="595" alt="image" src="https://github.com/user-attachments/assets/15e22088-15c9-415d-b401-431f52d58881" />


A secure REST API to register, monitor, and manage AI agents, featuring LLM-generated health summaries for each agent.

🚀 **Live Demo:** https://agentpulse-zuos.onrender.com
📖 **API Docs:** https://agentpulse-zuos.onrender.com/docs

## Overview

AgentPulse is a lightweight monitoring service for AI agent fleets. It exposes a JWT-secured REST API to register agents, track their status over time, and automatically generate human-readable health summaries using an LLM — useful as a backend for any dashboard that needs to keep tabs on a set of running AI agents.

## Features

- JWT-based authentication on every protected route
- Agent CRUD: register, fetch, update status, delete
- Full status-change history per agent (`status_logs`)
- AI-generated one-line health summaries via Groq
- Minimal HTML/CSS/JS dashboard served directly from the API
- SQLite for local development, PostgreSQL in production (auto-detected)

## Tech Stack

| Layer       | Technology                                        |
|-------------|----------------------------------------------------|
| Backend     | Python + FastAPI                                   |
| Database    | PostgreSQL (prod) / SQLite (dev) + SQLAlchemy ORM   |
| Auth        | JWT (Bearer token via python-jose)                  |
| Validation  | Pydantic schemas                                    |
| AI Summary  | Groq API (LLaMA 3)                                  |
| Dashboard   | Vanilla HTML/CSS/JS, served by FastAPI              |
| Deployment  | Render (`render.yaml`)                              |

## API Endpoints

| Method | Endpoint              | Auth | Description                            |
|--------|------------------------|------|------------------------------------------|
| POST   | `/auth/login`          | ❌   | Get a JWT token                          |
| POST   | `/agents`               | ✅   | Register a new agent                     |
| GET    | `/agents`               | ✅   | List all agents + AI health summaries    |
| GET    | `/agents/{id}`          | ✅   | Get a single agent                       |
| PATCH  | `/agents/{id}/status`   | ✅   | Update an agent's status                 |
| DELETE | `/agents/{id}`          | ✅   | Delete an agent                          |
| GET    | `/agents/{id}/logs`     | ✅   | Get full status-change history           |
| GET    | `/health`               | ❌   | Health check                             |

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL (optional — SQLite is used automatically if `DATABASE_URL` isn't set)

### 1. Set up the database (optional, for Postgres)
```sql
CREATE DATABASE agentpulse;
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Fill in your DB URL, JWT secret key, and Groq API key
```

### 3. Install and run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Open it
- Dashboard: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Demo login: `admin` / `password123`

## How It Works

1. **Auth** — `POST /auth/login` returns a JWT; every protected route expects it as a Bearer token.
2. **Database** — SQLAlchemy models map to tables that are auto-created on startup.
3. **Agent lifecycle** — agents are registered, their status updated over time, and every change is appended to `status_logs`.
4. **AI summaries** — an async `httpx` call sends agent status history to Groq with a structured prompt and returns a one-line health summary.

## Security Notes
- JWT required on all protected routes — no hardcoded credentials in source
- Secrets loaded from `.env` via `python-dotenv`; `.env` is gitignored
- All input validated via Pydantic schemas
- Passwords never returned in API responses

## Project Structure

## Groq API (Free Tier)
1. Sign up at https://console.groq.com
2. Create an API key
3. Add to `.env` as `GROQ_API_KEY=gsk_...`
4. Free tier: 14,400 requests/day, no credit card needed
