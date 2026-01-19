"""
FastAPI application for Strands Agent with session-based agent pooling.

Key features:
- Agent instances are cached per session (TTL: 10 minutes)
- Conversation history loaded from disk once per session
- Background cleanup of idle agents
- Real-time web search via Tavily
"""

import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.agent_pool import AgentPool
from app.models import ChatRequest, ChatResponse

# Global agent pool with 10-minute TTL
agent_pool = AgentPool(
    ttl_minutes=10,
    max_agents=100,
    session_dir=".sessions",
    window_size=10,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - start/stop agent pool."""
    await agent_pool.start()
    yield
    await agent_pool.stop()


app = FastAPI(
    title="Strands Agent API",
    description="AI Agent with persistent sessions and real-time web search",
    version="1.0.0",
    lifespan=lifespan,
)


def clean_response(text: str) -> str:
    """Remove thinking tags and clean up response text."""
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)
    return text.strip()


def extract_response_text(result) -> str:
    """Extract text content from agent result."""
    response_text = ""

    if hasattr(result, "message") and result.message:
        message = result.message
        content = (
            message.get("content")
            if isinstance(message, dict)
            else getattr(message, "content", [])
        )

        if content and isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    response_text += block["text"]
                elif hasattr(block, "text"):
                    response_text += block.text
        elif isinstance(content, str):
            response_text = content

    # Fallback if extraction fails
    if not response_text and result.message:
        response_text = str(result.message)

    return response_text


@app.get("/health")
async def health():
    """Health check endpoint with pool status."""
    return {
        "status": "healthy",
        "active_sessions": agent_pool.active_sessions,
        "sessions": agent_pool.session_ids,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the agent.

    The agent is cached per session_id. First request loads history from disk,
    subsequent requests (within 10 min) use the in-memory agent.
    """
    try:
        # Get cached agent or create new one
        agent = await agent_pool.get(request.session_id, request.model_provider)

        # Invoke agent (conversation already in memory)
        result = await agent.invoke_async(request.message)

        # Extract and clean response
        response_text = extract_response_text(result)

        return ChatResponse(
            response=clean_response(response_text),
            session_id=request.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """
    View conversation history for a session.

    Note: This reads from disk, not the in-memory agent.
    """
    try:
        from strands.session.file_session_manager import FileSessionManager

        session_manager = FileSessionManager(
            session_id=session_id,
            storage_dir=".sessions",
        )

        try:
            messages = session_manager.list_messages(
                session_id=session_id, agent_id="default"
            )
            return {"session_id": session_id, "messages": messages}
        except Exception:
            return {"session_id": session_id, "messages": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
async def delete_session(session_id: str, provider: str = "nova-lite"):
    """
    Remove an agent from the pool (does not delete disk history).

    Useful for forcing a fresh agent on next request.
    """
    await agent_pool.remove(session_id, provider)
    return {"status": "removed", "session_id": session_id}
