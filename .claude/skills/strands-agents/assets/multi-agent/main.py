#!/usr/bin/env python3
"""Multi-Agent Swarm Example with Strands."""

from strands import Agent
from strands.multiagent import Swarm


def create_research_swarm():
    """Create a research swarm with specialized agents."""

    # Research agent - gathers information
    researcher = Agent(
        name="researcher",
        system_prompt="""You are a research specialist.
        Your role is to:
        - Gather comprehensive information on topics
        - Identify key facts and data points
        - Organize findings clearly

        When research is complete, hand off to the writer."""
    )

    # Writer agent - creates content
    writer = Agent(
        name="writer",
        system_prompt="""You are a technical writer.
        Your role is to:
        - Take research findings and create clear summaries
        - Structure information logically
        - Use simple, accessible language

        When writing is complete, hand off to the reviewer."""
    )

    # Reviewer agent - quality control
    reviewer = Agent(
        name="reviewer",
        system_prompt="""You are a quality reviewer.
        Your role is to:
        - Check accuracy and completeness
        - Verify clarity and readability
        - Approve final output or request revisions

        Provide the final approved output."""
    )

    # Create swarm with safety limits
    swarm = Swarm(
        agents=[researcher, writer, reviewer],
        entry_point=researcher,
        max_handoffs=10,
        max_iterations=15,
        execution_timeout=300.0,  # 5 minutes total
        node_timeout=120.0,       # 2 minutes per agent
    )

    return swarm


def main():
    swarm = create_research_swarm()

    # Run the swarm on a task
    result = swarm.run(
        "Explain the key concepts of machine learning in a way that's "
        "accessible to someone without a technical background."
    )

    print(f"Status: {result.status}")
    print(f"Agent flow: {' -> '.join(result.node_history)}")
    print(f"\nFinal output:\n{result.output}")


if __name__ == "__main__":
    main()
