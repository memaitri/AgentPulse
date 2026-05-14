import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"

async def generate_health_summary(agent_name: str, agent_type: str, status: str, recent_logs: list[str]) -> str:
    """Call Groq API to generate a one-line health summary for an agent."""
    
    if not GROQ_API_KEY:
        return f"Agent '{agent_name}' is currently {status}. (Configure GROQ_API_KEY for AI summaries)"

    log_text = ", ".join(recent_logs[-5:]) if recent_logs else "no recent activity"
    prompt = (
        f"You are a monitoring system. Generate a single concise sentence (max 20 words) "
        f"summarizing the health of an AI agent.\n"
        f"Agent: {agent_name} | Type: {agent_type} | Current Status: {status} | "
        f"Recent status history: {log_text}\n"
        f"Respond with only the summary sentence, no extra text."
    )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 60,
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Agent '{agent_name}' is {status}. (LLM unavailable: {str(e)[:50]})"
