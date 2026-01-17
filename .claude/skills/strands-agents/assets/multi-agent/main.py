"""
Multi-Agent Workflow Example

Demonstrates sequential workflow with specialized agents.
"""

from strands import Agent

# Create specialized agents
researcher = Agent(
    system_prompt="""You are a research specialist.

    Your role:
    - Find accurate information about the given topic
    - Identify key facts, trends, and developments
    - Present findings in a structured format with bullet points
    - Be concise and factual
    """,
    callback_handler=None  # Silent mode
)

analyst = Agent(
    system_prompt="""You are a data analyst.

    Your role:
    - Analyze research findings and extract insights
    - Identify patterns and trends
    - Provide clear analysis with key takeaways
    - Be analytical and objective
    """,
    callback_handler=None  # Silent mode
)

writer = Agent(
    system_prompt="""You are a professional writer.

    Your role:
    - Create clear, engaging content based on analysis
    - Organize information logically
    - Write in a professional yet accessible tone
    - Create polished final reports
    """
)

def process_workflow(topic: str) -> str:
    """
    Process a topic through the research-analyze-write pipeline.

    Args:
        topic: The topic to research and report on

    Returns:
        Final polished report
    """
    print(f"\n{'='*60}")
    print(f"Processing workflow for: {topic}")
    print(f"{'='*60}\n")

    # Step 1: Research
    print("Step 1/3: Researching...")
    research_results = researcher(
        f"Research the latest developments in {topic}. "
        f"Provide 5-7 key facts or findings."
    )
    print(f"✓ Research completed ({len(research_results.message)} characters)\n")

    # Step 2: Analysis
    print("Step 2/3: Analyzing...")
    analysis = analyst(
        f"Analyze these research findings and extract 3-5 key insights:\n\n"
        f"{research_results.message}"
    )
    print(f"✓ Analysis completed ({len(analysis.message)} characters)\n")

    # Step 3: Report writing
    print("Step 3/3: Writing final report...")
    final_report = writer(
        f"Create a professional report (3-4 paragraphs) based on this analysis:\n\n"
        f"{analysis.message}\n\n"
        f"Original topic: {topic}"
    )
    print(f"✓ Report completed\n")

    return final_report.message

def main():
    print("=" * 60)
    print("Multi-Agent Workflow Example")
    print("=" * 60)

    # Example topics
    example_topics = [
        "artificial intelligence in healthcare",
        "renewable energy trends",
        "remote work productivity"
    ]

    print("\nExample topics:")
    for i, topic in enumerate(example_topics, 1):
        print(f"{i}. {topic}")

    # Get user input
    print("\nEnter a topic to research (or select 1-3 from above):")
    user_input = input("Topic: ").strip()

    # Handle selection or custom topic
    if user_input.isdigit() and 1 <= int(user_input) <= len(example_topics):
        topic = example_topics[int(user_input) - 1]
    elif user_input:
        topic = user_input
    else:
        topic = example_topics[0]  # Default

    # Process through workflow
    final_report = process_workflow(topic)

    # Display final result
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(final_report)
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
