#!/usr/bin/env python3
"""Strands Agent with Custom Tools Example."""

from strands import Agent, tool
from strands_tools import calculator, current_time


@tool
def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: Name of the city to get weather for
    """
    # Replace with actual weather API call
    return f"Weather in {city}: Sunny, 72°F (22°C)"


@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the database for information.

    Args:
        query: Search query string
        limit: Maximum number of results to return
    """
    # Replace with actual database query
    return f"Found {limit} results for '{query}': [sample data]"


def main():
    # Create agent with built-in and custom tools
    agent = Agent(
        system_prompt="""You are a helpful assistant with access to:
        - Weather information
        - Database search
        - Calculator
        - Current time

        Use the appropriate tool based on user requests.""",
        tools=[get_weather, search_database, calculator, current_time]
    )

    # Example queries
    queries = [
        "What's the weather in Seattle?",
        "What time is it now?",
        "Calculate 15% of 230",
        "Search the database for recent orders",
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = agent(query)
        print(f"Agent: {response.message}")


if __name__ == "__main__":
    main()
