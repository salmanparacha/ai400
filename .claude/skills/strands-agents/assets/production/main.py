#!/usr/bin/env python3
"""Production-Ready Strands Agent with all best practices."""

import os
import time
import logging
from typing import Optional

from pydantic import BaseModel, Field
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands.hooks import (
    HookProvider,
    HookRegistry,
    BeforeInvocationEvent,
    AfterInvocationEvent,
    BeforeToolCallEvent,
)
from strands.telemetry import StrandsTelemetry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Structured Output Models
# ============================================================================

class TaskResult(BaseModel):
    """Structured output for task completion."""
    status: str = Field(description="'success' or 'error'")
    result: str = Field(description="The task result or error message")
    confidence: float = Field(description="Confidence score 0-1", ge=0, le=1)


# ============================================================================
# Custom Tools
# ============================================================================

@tool
def get_user_data(user_id: str) -> str:
    """Retrieve user data from the database.

    Args:
        user_id: The unique user identifier
    """
    try:
        # Replace with actual database call
        return f"User {user_id}: name=John Doe, email=john@example.com"
    except Exception as e:
        return f"Error fetching user: {str(e)}"


@tool
def process_order(order_id: str, action: str) -> str:
    """Process an order with the specified action.

    Args:
        order_id: The order identifier
        action: Action to perform (view, update, cancel)
    """
    valid_actions = ["view", "update", "cancel"]
    if action not in valid_actions:
        return f"Invalid action. Use one of: {valid_actions}"

    # Replace with actual order processing
    return f"Order {order_id}: {action} completed successfully"


# ============================================================================
# Lifecycle Hooks
# ============================================================================

class MetricsHook(HookProvider):
    """Track request metrics and performance."""

    def __init__(self):
        self.request_count = 0
        self.start_time: Optional[float] = None

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.on_request_start)
        registry.add_callback(AfterInvocationEvent, self.on_request_end)

    def on_request_start(self, event: BeforeInvocationEvent) -> None:
        self.request_count += 1
        self.start_time = time.time()
        logger.info(f"Request #{self.request_count} started")

    def on_request_end(self, event: AfterInvocationEvent) -> None:
        duration = time.time() - (self.start_time or time.time())
        logger.info(f"Request completed in {duration:.2f}s")


class RateLimitHook(HookProvider):
    """Limit tool calls per request."""

    def __init__(self, max_tools: int = 10):
        self.max_tools = max_tools
        self.tool_count = 0

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.reset_count)
        registry.add_callback(BeforeToolCallEvent, self.check_limit)

    def reset_count(self, event: BeforeInvocationEvent) -> None:
        self.tool_count = 0

    def check_limit(self, event: BeforeToolCallEvent) -> None:
        self.tool_count += 1
        if self.tool_count > self.max_tools:
            logger.warning(f"Tool limit ({self.max_tools}) exceeded")
            event.cancel_tool = True


# ============================================================================
# Agent Factory
# ============================================================================

def create_production_agent(
    session_id: str,
    guardrail_id: Optional[str] = None,
    enable_telemetry: bool = True,
) -> Agent:
    """Create a production-ready agent with all best practices.

    Args:
        session_id: Unique session identifier for conversation persistence
        guardrail_id: Optional Bedrock guardrail ID
        enable_telemetry: Whether to enable observability

    Returns:
        Configured Agent instance
    """

    # Configure model with optional guardrails
    model_config = {
        "model_id": os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-sonnet-4-20250514-v1:0"
        ),
        "temperature": 0.3,
        "max_tokens": 2048,
    }

    if guardrail_id:
        model_config.update({
            "guardrail_id": guardrail_id,
            "guardrail_version": os.getenv("GUARDRAIL_VERSION", "1"),
            "guardrail_trace": "enabled",
        })

    model = BedrockModel(**model_config)

    # Setup session persistence
    session_manager = FileSessionManager(session_id=session_id)

    # Setup telemetry
    if enable_telemetry:
        telemetry = StrandsTelemetry()
        telemetry.setup_console_exporter()
        # telemetry.setup_otlp_exporter()  # Uncomment for OTLP

    # Create agent with all components
    agent = Agent(
        model=model,
        system_prompt="""You are a helpful customer service assistant.

        You can:
        - Look up user information
        - Process orders (view, update, cancel)

        Always be polite and helpful. If you're unsure, ask for clarification.
        Never share sensitive information without verification.""",
        tools=[get_user_data, process_order],
        session_manager=session_manager,
        hooks=[MetricsHook(), RateLimitHook(max_tools=10)],
    )

    return agent


# ============================================================================
# Main Application
# ============================================================================

def main():
    # Create agent with session persistence
    agent = create_production_agent(
        session_id="demo-session-001",
        enable_telemetry=True,
    )

    # Example: Simple query
    print("\n--- Simple Query ---")
    response = agent("Hello! Can you help me with my order?")
    print(f"Agent: {response.message}")

    # Example: Tool use
    print("\n--- Tool Use ---")
    response = agent("Can you look up user U12345?")
    print(f"Agent: {response.message}")

    # Example: Structured output
    print("\n--- Structured Output ---")
    result = agent.structured_output(
        TaskResult,
        "Summarize what you can help with and rate your confidence."
    )
    print(f"Status: {result.status}")
    print(f"Result: {result.result}")
    print(f"Confidence: {result.confidence}")


if __name__ == "__main__":
    main()
