# Multi-Agent Patterns

This reference covers patterns for building multi-agent systems with Strands, including sequential workflows, parallel processing, and agent collaboration.

## Table of Contents

- [Sequential Workflow Pattern](#sequential-workflow-pattern)
- [Specialized Agent Roles](#specialized-agent-roles)
- [Data Passing Between Agents](#data-passing-between-agents)
- [Error Handling in Workflows](#error-handling-in-workflows)
- [Best Practices](#best-practices)

## Sequential Workflow Pattern

Create a pipeline where each agent processes data in sequence:

```python
from strands import Agent

# Create specialized agents
researcher = Agent(
    system_prompt="You are a research specialist. Find key information about topics.",
    callback_handler=None
)

analyst = Agent(
    system_prompt="You analyze research data and extract insights.",
    callback_handler=None
)

writer = Agent(
    system_prompt="You create polished reports based on analysis."
)

def process_workflow(topic):
    """Process a topic through the research-analyze-write pipeline."""
    # Step 1: Research
    research_results = researcher(f"Research the latest developments in {topic}")

    # Step 2: Analysis
    analysis = analyst(f"Analyze these research findings: {research_results}")

    # Step 3: Report writing
    final_report = writer(f"Create a report based on this analysis: {analysis}")

    return final_report

# Use the workflow
report = process_workflow("artificial intelligence")
```

**Key points:**
- Each agent has a specialized system prompt
- Output from one agent becomes input to the next
- Linear data flow: research → analysis → writing

## Specialized Agent Roles

### Research Agent

```python
research_agent = Agent(
    system_prompt="""You are a research specialist.

    Your role:
    - Find accurate information about the given topic
    - Identify key facts, trends, and developments
    - Cite sources when possible
    - Present findings in a structured format
    """,
    tools=[web_search, read_file]  # Hypothetical tools
)
```

### Data Analyst Agent

```python
from strands_tools import calculator

analyst_agent = Agent(
    system_prompt="""You are a data analyst.

    Your role:
    - Analyze quantitative and qualitative data
    - Identify patterns and trends
    - Perform calculations and statistical analysis
    - Present insights clearly
    """,
    tools=[calculator, data_processor]  # Hypothetical data_processor
)
```

### Code Review Agent

```python
reviewer_agent = Agent(
    system_prompt="""You are a code reviewer.

    Your role:
    - Review code for bugs, security issues, and best practices
    - Suggest improvements
    - Check for code style and conventions
    - Provide constructive feedback
    """,
    tools=[file_reader, linter]  # Hypothetical tools
)
```

### Content Writer Agent

```python
writer_agent = Agent(
    system_prompt="""You are a professional writer.

    Your role:
    - Create clear, engaging content
    - Maintain consistent tone and style
    - Organize information logically
    - Ensure proper grammar and formatting
    """
)
```

## Data Passing Between Agents

### Simple Pass-Through

```python
def two_step_process(query):
    # First agent processes input
    result1 = agent1(query)

    # Second agent processes first agent's output
    result2 = agent2(result1)

    return result2
```

### Structured Data Passing

```python
import json

def structured_workflow(topic):
    # Research agent returns structured data
    research_prompt = f"""Research {topic} and return findings in this JSON format:
    {{
        "key_facts": [],
        "trends": [],
        "sources": []
    }}
    """
    research_json = researcher(research_prompt)

    # Parse and use structured data
    research_data = json.loads(research_json)

    # Analyst receives structured input
    analysis_prompt = f"""Analyze these findings:
    Facts: {research_data['key_facts']}
    Trends: {research_data['trends']}
    """
    analysis = analyst(analysis_prompt)

    return analysis
```

### Context Accumulation

```python
def accumulating_workflow(task):
    context = {"task": task, "steps": []}

    # Step 1: Planning
    plan = planner(f"Create a plan for: {task}")
    context["plan"] = plan
    context["steps"].append("planning")

    # Step 2: Execution (with context)
    execution = executor(f"""Execute this plan: {plan}

    Original task: {context['task']}
    """)
    context["execution"] = execution
    context["steps"].append("execution")

    # Step 3: Review (with full context)
    review = reviewer(f"""Review this work:

    Task: {context['task']}
    Plan: {context['plan']}
    Execution: {context['execution']}
    """)

    return review
```

## Error Handling in Workflows

### Retry Logic

```python
def workflow_with_retry(topic, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Step 1
            research = researcher(f"Research {topic}")

            # Step 2
            analysis = analyst(f"Analyze: {research}")

            # Step 3
            report = writer(f"Write report: {analysis}")

            return report
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                continue
            else:
                print(f"All attempts failed")
                raise
```

### Validation Between Steps

```python
def validated_workflow(data):
    # Step 1: Process
    result1 = processor(f"Process this data: {data}")

    # Validate before next step
    if not is_valid(result1):
        # Retry with more specific instructions
        result1 = processor(f"Process this data more carefully: {data}. Ensure output is valid.")

    # Step 2: Continue with validated data
    result2 = analyzer(f"Analyze: {result1}")

    return result2

def is_valid(result):
    """Validate agent output meets requirements."""
    # Check for minimum length, required fields, etc.
    return len(result) > 100 and "error" not in result.lower()
```

### Fallback Agents

```python
def workflow_with_fallback(query):
    try:
        # Try specialized agent first
        return specialist_agent(query)
    except Exception as e:
        print(f"Specialist failed: {e}, falling back to generalist")
        # Fallback to general-purpose agent
        return general_agent(query)
```

## Best Practices

### 1. Clear Agent Responsibilities

Each agent should have a well-defined role:

```python
# Good: Clear specialization
data_collector = Agent(system_prompt="Collect and organize data")
data_analyzer = Agent(system_prompt="Analyze data and find insights")

# Avoid: Overlapping responsibilities
agent1 = Agent(system_prompt="Collect and analyze data")  # Too broad
agent2 = Agent(system_prompt="Process data")  # Too vague
```

### 2. Minimize Context Size

Pass only necessary information between agents:

```python
# Good: Pass only what's needed
summary = agent1(task)
result = agent2(f"Review this summary: {summary}")

# Avoid: Passing entire conversation history
full_history = agent1.get_full_history()  # Could be very large
result = agent2(f"Review everything: {full_history}")
```

### 3. Use System Prompts Effectively

System prompts define agent behavior:

```python
# Good: Specific, actionable system prompt
Agent(system_prompt="""You are a Python code reviewer.
Focus on:
- Security vulnerabilities
- Performance issues
- PEP 8 compliance
- Error handling

Provide specific line numbers and suggested fixes.""")

# Avoid: Vague system prompt
Agent(system_prompt="You help with code")
```

### 4. Parallel Processing When Possible

For independent tasks, consider parallel execution:

```python
import concurrent.futures

def parallel_research(topics):
    """Research multiple topics in parallel."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all research tasks
        futures = {
            executor.submit(researcher, f"Research {topic}"): topic
            for topic in topics
        }

        # Collect results
        results = {}
        for future in concurrent.futures.as_completed(futures):
            topic = futures[future]
            results[topic] = future.result()

    return results

# Later, analyze combined results
combined = "\n\n".join(results.values())
analysis = analyst(f"Analyze these research findings: {combined}")
```

### 5. Log Agent Interactions

Track workflow progress for debugging:

```python
import logging

logger = logging.getLogger(__name__)

def logged_workflow(task):
    logger.info(f"Starting workflow for: {task}")

    logger.info("Step 1: Research")
    research = researcher(task)
    logger.info(f"Research completed: {len(research)} chars")

    logger.info("Step 2: Analysis")
    analysis = analyst(research)
    logger.info(f"Analysis completed: {len(analysis)} chars")

    logger.info("Step 3: Report")
    report = writer(analysis)
    logger.info(f"Report completed: {len(report)} chars")

    return report
```

### 6. Design for Failure

Assume any step can fail:

```python
def robust_workflow(task):
    results = {}

    # Step 1: Try primary approach
    try:
        results["research"] = primary_researcher(task)
    except Exception:
        # Fallback to simpler approach
        results["research"] = basic_researcher(task)

    # Step 2: Continue even if previous step partial
    if results.get("research"):
        try:
            results["analysis"] = analyst(results["research"])
        except Exception as e:
            results["analysis_error"] = str(e)

    # Step 3: Generate report from available data
    available_data = {k: v for k, v in results.items() if not k.endswith("_error")}
    report = writer(f"Create report from: {available_data}")

    return report
```
