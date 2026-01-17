"""
Production Strands Agent Example

Production-ready agent with:
- AWS Bedrock model configuration
- Comprehensive error handling
- Structured logging
- Metrics collection
- Environment-based configuration
"""

import os
import logging
import json
import time
from datetime import datetime
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect agent execution metrics."""

    def __init__(self):
        self.start_time = None
        self.tool_calls = []
        self.response_length = 0
        self.tool_use_ids = set()

    def __call__(self, **kwargs):
        """Callback handler for metrics collection."""
        if self.start_time is None:
            self.start_time = time.time()

        if "data" in kwargs:
            # Track response length
            self.response_length += len(kwargs["data"])
            # Also print the output
            print(kwargs["data"], end="")

        elif "current_tool_use" in kwargs:
            tool = kwargs["current_tool_use"]
            tool_id = tool.get("toolUseId")

            # Only count unique tool uses
            if tool_id and tool_id not in self.tool_use_ids:
                self.tool_use_ids.add(tool_id)
                self.tool_calls.append({
                    "name": tool.get("name"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "input": tool.get("input", {})
                })
                print(f"\n[Using tool: {tool.get('name')}]\n")

    def get_metrics(self):
        """Return collected metrics."""
        execution_time = time.time() - self.start_time if self.start_time else 0
        return {
            "execution_time_seconds": round(execution_time, 2),
            "tool_calls_count": len(self.tool_calls),
            "tools_used": self.tool_calls,
            "response_length_chars": self.response_length
        }

    def log_metrics(self):
        """Log metrics to logger."""
        metrics = self.get_metrics()
        logger.info(f"Agent metrics: {json.dumps(metrics, indent=2)}")

def create_bedrock_model():
    """
    Create Bedrock model configuration from environment variables.

    Environment variables:
    - AWS_REGION: AWS region (default: us-east-1)
    - MODEL_TEMPERATURE: Model temperature (default: 0.3)
    - MODEL_MAX_TOKENS: Max tokens (default: 4096)
    """
    region = os.getenv("AWS_REGION", "us-east-1")
    temperature = float(os.getenv("MODEL_TEMPERATURE", "0.3"))
    max_tokens = int(os.getenv("MODEL_MAX_TOKENS", "4096"))

    logger.info(f"Configuring Bedrock model - Region: {region}, "
                f"Temperature: {temperature}, Max tokens: {max_tokens}")

    return BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region=region,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=0.9
    )

def create_agent():
    """
    Create production agent with error handling.

    Returns:
        Configured Agent instance or None if creation fails
    """
    try:
        # Try Bedrock first
        model = create_bedrock_model()
        metrics = MetricsCollector()

        agent = Agent(
            model=model,
            tools=[calculator, current_time],
            system_prompt="""You are a helpful production assistant.

            Guidelines:
            - Provide accurate, concise responses
            - Use tools when appropriate
            - Handle errors gracefully
            - Always verify your calculations
            """,
            callback_handler=metrics
        )

        logger.info("Agent created successfully with Bedrock model")
        return agent, metrics

    except Exception as e:
        logger.error(f"Failed to create Bedrock agent: {e}")
        logger.info("Falling back to simple model configuration")

        try:
            # Fallback to simple model
            metrics = MetricsCollector()
            agent = Agent(
                model="claude-3-5-sonnet-20241022",
                tools=[calculator, current_time],
                system_prompt="""You are a helpful production assistant.

                Guidelines:
                - Provide accurate, concise responses
                - Use tools when appropriate
                - Handle errors gracefully
                - Always verify your calculations
                """,
                callback_handler=metrics
            )

            logger.info("Agent created with fallback model")
            return agent, metrics

        except Exception as fallback_error:
            logger.error(f"Failed to create fallback agent: {fallback_error}")
            return None, None

def process_query(agent, metrics, query: str) -> dict:
    """
    Process a query with comprehensive error handling and logging.

    Args:
        agent: Configured Agent instance
        metrics: MetricsCollector instance
        query: User query to process

    Returns:
        Dictionary with status, response, and metrics
    """
    logger.info(f"Processing query: {query}")

    try:
        # Reset metrics for this query
        metrics.start_time = time.time()
        metrics.tool_calls = []
        metrics.response_length = 0
        metrics.tool_use_ids = set()

        # Process query
        response = agent(query)

        # Log success
        logger.info("Query processed successfully")
        metrics.log_metrics()

        return {
            "status": "success",
            "query": query,
            "response": response.message,
            "metrics": metrics.get_metrics()
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return {
            "status": "error",
            "query": query,
            "error": str(e),
            "metrics": metrics.get_metrics()
        }

def main():
    logger.info("Starting production Strands agent")

    print("=" * 60)
    print("Production Strands Agent")
    print("=" * 60)

    # Create agent
    agent, metrics = create_agent()

    if agent is None:
        print("\nError: Failed to create agent. Check logs for details.")
        return

    print(f"\n✓ Agent initialized successfully")
    print(f"✓ Logging to: agent.log\n")

    # Example queries
    example_queries = [
        "What is the current time?",
        "Calculate 3111696 / 74088",
        "What is 15% of 450?",
    ]

    results = []

    for i, query in enumerate(example_queries, 1):
        print(f"\n{'-'*60}")
        print(f"Query {i}: {query}")
        print(f"{'-'*60}\n")

        result = process_query(agent, metrics, query)
        results.append(result)

        if result["status"] == "success":
            print(f"\n\nMetrics: {json.dumps(result['metrics'], indent=2)}\n")
        else:
            print(f"\nError: {result['error']}\n")

    # Interactive mode
    print(f"\n{'='*60}")
    print("Interactive mode (press Enter to exit)")
    print(f"{'='*60}\n")

    while True:
        user_query = input("Your question: ").strip()
        if not user_query:
            break

        print()
        result = process_query(agent, metrics, user_query)
        if result["status"] == "success":
            print(f"\n\nMetrics: {json.dumps(result['metrics'], indent=2)}\n")
        else:
            print(f"\nError: {result['error']}\n")

    # Summary
    logger.info(f"Session completed. Processed {len(results)} queries")
    print(f"\n{'='*60}")
    print(f"Session complete. Check agent.log for detailed logs.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
