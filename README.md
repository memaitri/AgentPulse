# AgentPulse — Mini Agent Monitor API
### Hapticware Hackathon Submission

A secure REST API to register, monitor, and manage AI agents, with LLM-generated health summaries.

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python + FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Auth | JWT (Bearer token via python-jose) |
| AI Summary | Groq API (llama3-8b-8192) |
| Dashboard | Vanilla HTML/CSS/JS served by FastAPI |

---

## Quick Start

### 1. PostgreSQL Setup
```sql
-- Run in psql:
CREATE DATABASE agentpulse;
```

### 2. Environment Variables
```bash
cp .env.example .env
# Edit .env with your DB URL, secret key, and Groq API key
```

### 3. Install & Run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Open
- **Dashboard UI:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Login:** username: `admin`, password: `password123`

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/login` | ❌ | Get JWT token |
| POST | `/agents` | ✅ | Register new agent |
| GET | `/agents` | ✅ | Get all agents + AI health summaries |
| GET | `/agents/{id}` | ✅ | Get single agent |
| PATCH | `/agents/{id}/status` | ✅ | Update agent status |
| DELETE | `/agents/{id}` | ✅ | Delete agent |
| GET | `/agents/{id}/logs` | ✅ | Get full status history |
| GET | `/health` | ❌ | Health check |

---

## Security Practices
- JWT tokens on every protected route (no hardcoded credentials in source)
- All secrets loaded from `.env` via `python-dotenv`
- `.env` is gitignored
- Input validation via Pydantic schemas
- Password never stored in plain text in responses

---

## Walkthrough Notes (10-min verbal)

1. **Project structure** — each file has one responsibility
2. **Auth flow** — POST /auth/login → JWT → Bearer token in all headers
3. **Database** — SQLAlchemy models map to PostgreSQL tables, auto-created on startup
4. **Agent CRUD** — register, update status, delete; status changes logged in status_logs table
5. **LLM Integration** — async httpx call to Groq with a structured prompt, returns one-line health summary
6. **Dashboard** — pure HTML/JS frontend served from /static, uses fetch() with Bearer token
7. **Error handling** — HTTP exceptions with appropriate status codes throughout

---

## Groq API (Free Tier)
1. Sign up at https://console.groq.com
2. Create an API key
3. Add to `.env` as `GROQ_API_KEY=gsk_...`
4. Free tier: 14,400 requests/day, no credit card needed
