#!/usr/bin/env python3
"""Minimal Strands Agent - Hello World Example."""

from strands import Agent

def main():
    # Create a basic agent (uses Bedrock by default)
    agent = Agent(
        system_prompt="You are a helpful assistant."
    )

    # Simple conversation
    response = agent("Hello! What can you help me with?")
    print(response.message)


if __name__ == "__main__":
    main()
