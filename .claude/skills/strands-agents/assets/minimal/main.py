"""
Minimal Strands Agent Example

A simple agent using built-in tools.
"""

from strands import Agent
from strands_tools import calculator, current_time

def main():
    # Create agent with built-in tools
    agent = Agent(tools=[calculator, current_time])

    # Example queries
    print("=" * 50)
    print("Minimal Strands Agent Example")
    print("=" * 50)

    # Query 1: Time
    print("\n1. What is the current time?")
    response1 = agent("What is the time right now?")
    print(f"Response: {response1.message}\n")

    # Query 2: Calculation
    print("2. Calculate 3111696 / 74088")
    response2 = agent("Calculate 3111696 / 74088")
    print(f"Response: {response2.message}\n")

    # Query 3: Interactive
    print("3. Interactive mode - ask your own question:")
    user_query = input("Your question: ")
    if user_query.strip():
        response3 = agent(user_query)
        print(f"Response: {response3.message}")

if __name__ == "__main__":
    main()
