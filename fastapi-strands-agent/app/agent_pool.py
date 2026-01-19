"""
Agent Pool with TTL-based lifecycle management.

This module manages Strands Agent instances with:
- Session-based caching (agents stay in memory for active conversations)
- TTL eviction (agents removed after idle timeout)
- LRU eviction (oldest agent removed when at capacity)
- Thread-safe async operations
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands_tools import tavily

load_dotenv()

logger = logging.getLogger(__name__)


class AgentPool:
    """
    Manages agent instances with TTL-based lifecycle.

    - Agents are created on first request for a session
    - Agents stay in memory for `ttl_minutes` after last access
    - Background task cleans up expired agents
    - Thread-safe with asyncio.Lock

    This avoids the overhead of:
    - Reading full conversation history from disk on every request
    - Recreating Agent/Model/SessionManager objects per request
    """

    def __init__(
        self,
        ttl_minutes: int = 10,
        max_agents: int = 100,
        session_dir: str = ".sessions",
        window_size: int = 10,
    ):
        """
        Initialize the agent pool.

        Args:
            ttl_minutes: How long an idle agent stays in memory
            max_agents: Maximum number of concurrent agents
            session_dir: Directory for conversation persistence
            window_size: Sliding window size for conversation context
        """
        self._agents: Dict[str, Tuple[Agent, datetime]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
        self._max_agents = max_agents
        self._session_dir = session_dir
        self._window_size = window_size
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start background cleanup task. Call this on app startup."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(
            f"AgentPool started: ttl={self._ttl.seconds // 60}min, "
            f"max_agents={self._max_agents}"
        )

    async def stop(self):
        """Stop cleanup and clear all agents. Call this on app shutdown."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        self._agents.clear()
        logger.info("AgentPool stopped, all agents cleared")

    async def get(self, session_id: str, provider: str = "nova-lite") -> Agent:
        """
        Get or create an agent for the session.

        If an agent exists for this session, returns it and updates last access time.
        Otherwise, creates a new agent (which loads history from disk once).

        Args:
            session_id: Unique session identifier
            provider: Model provider ("nova-lite", "anthropic", or model ID)

        Returns:
            Agent instance for the session
        """
        cache_key = f"{session_id}:{provider}"

        async with self._lock:
            if cache_key in self._agents:
                agent, _ = self._agents[cache_key]
                # Update last access time
                self._agents[cache_key] = (agent, datetime.now())
                logger.debug(f"Reusing cached agent for session: {session_id}")
                return agent

            # Evict oldest if at capacity
            if len(self._agents) >= self._max_agents:
                await self._evict_oldest()

            # Create new agent (reads history from disk once)
            agent = self._create_agent(session_id, provider)
            self._agents[cache_key] = (agent, datetime.now())
            logger.info(f"Created new agent for session: {session_id}")
            return agent

    def _create_agent(self, session_id: str, provider: str) -> Agent:
        """Factory method to create a new agent."""
        model = self._get_model(provider)

        if not os.getenv("TAVILY_API_KEY"):
            logger.warning("TAVILY_API_KEY not set. Web search will fail.")

        session_manager = FileSessionManager(
            session_id=session_id,
            storage_dir=self._session_dir,
        )

        conversation_manager = SlidingWindowConversationManager(
            window_size=self._window_size,
            per_turn=True,
        )

        return Agent(
            model=model,
            session_manager=session_manager,
            conversation_manager=conversation_manager,
            tools=[tavily],
            system_prompt=(
                "You are a professional AI assistant with REAL-TIME web access. "
                "You have a tool named 'tavily_search' available to you. "
                "Whenever a user asks for current events, news, or information you don't know, "
                "you MUST invoke 'tavily_search' with a 'query' argument. "
                "CRITICAL: Do not mention the tool names like 'tavily_search' in your final response. "
                "Simply present the information naturally as your own findings. "
                "Do not apologize or say you cannot search; just use the tool."
            ),
        )

    def _get_model(self, provider: str) -> BedrockModel:
        """Get model instance for provider."""
        model_ids = {
            "nova-lite": "amazon.nova-lite-v1:0",
            "anthropic": "anthropic.claude-3-sonnet-20240229-v1:0",
        }
        model_id = model_ids.get(provider, provider)
        return BedrockModel(model_id=model_id)

    async def _cleanup_loop(self):
        """Background task to remove expired agents periodically."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            await self._cleanup_expired()

    async def _cleanup_expired(self):
        """Remove agents that haven't been accessed within TTL."""
        async with self._lock:
            now = datetime.now()
            expired = [
                key
                for key, (_, last_access) in self._agents.items()
                if now - last_access > self._ttl
            ]
            for key in expired:
                del self._agents[key]
                logger.info(f"Evicted expired agent: {key}")

    async def _evict_oldest(self):
        """Evict the least recently used agent when at capacity."""
        if not self._agents:
            return
        oldest_key = min(
            self._agents.keys(),
            key=lambda k: self._agents[k][1],
        )
        del self._agents[oldest_key]
        logger.info(f"Evicted oldest agent (capacity limit): {oldest_key}")

    async def remove(self, session_id: str, provider: str = "nova-lite"):
        """Manually remove an agent from the pool."""
        cache_key = f"{session_id}:{provider}"
        async with self._lock:
            if cache_key in self._agents:
                del self._agents[cache_key]
                logger.info(f"Manually removed agent: {cache_key}")

    @property
    def active_sessions(self) -> int:
        """Number of active agent sessions in memory."""
        return len(self._agents)

    @property
    def session_ids(self) -> list[str]:
        """List of active session IDs."""
        return [key.split(":")[0] for key in self._agents.keys()]
