# Multi-Agent Systems Reference

## Quick Start: Swarm Tool

Simplest way to enable multi-agent collaboration:

```python
from strands import Agent
from strands_tools import swarm

agent = Agent(
    tools=[swarm],
    system_prompt="Create a swarm of agents to solve complex queries."
)

agent("Research, analyze, and summarize quantum computing advances")
```

---

## Explicit Swarm Configuration

For fine-grained control over agent orchestration:

```python
from strands import Agent
from strands.multiagent import Swarm

# Define specialized agents
researcher = Agent(
    name="researcher",
    system_prompt="""You are a research specialist.
    - Gather facts and data on topics
    - Cite sources when possible
    - Hand off to writer when research is complete"""
)

writer = Agent(
    name="writer",
    system_prompt="""You are a technical writer.
    - Create clear, concise summaries
    - Structure information logically
    - Use the research provided"""
)

reviewer = Agent(
    name="reviewer",
    system_prompt="""You are a quality reviewer.
    - Check accuracy and clarity
    - Suggest improvements
    - Approve final output"""
)

# Configure swarm
swarm = Swarm(
    agents=[researcher, writer, reviewer],
    entry_point=researcher,
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,
    node_timeout=300.0,
)

# Execute
result = swarm.run("Explain machine learning in simple terms")
print(result.status)       # "completed" or "failed"
print(result.node_history) # Trace of agent handoffs
```

---

## Swarm Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agents` | List[Agent] | Required | Agents participating in swarm |
| `entry_point` | Agent | First agent | Starting agent |
| `max_handoffs` | int | 20 | Max agent-to-agent transfers |
| `max_iterations` | int | 20 | Max total iterations |
| `execution_timeout` | float | 900.0 | Total timeout (seconds) |
| `node_timeout` | float | 300.0 | Per-agent timeout (seconds) |
| `repetitive_handoff_detection_window` | int | 0 | Window for ping-pong detection |
| `repetitive_handoff_min_unique_agents` | int | 0 | Min unique agents in window |

---

## Agent Handoff Patterns

### Explicit Handoff Instructions

```python
coordinator = Agent(
    name="coordinator",
    system_prompt="""You coordinate tasks between specialists.

    Available agents:
    - researcher: For gathering information
    - coder: For writing code
    - reviewer: For quality checks

    Hand off to the appropriate agent based on the current need.
    When all tasks complete, summarize and finish."""
)
```

### Tool-Based Handoff

```python
from strands import Agent, tool

@tool
def handoff_to_researcher(topic: str) -> str:
    """Hand off to researcher for information gathering."""
    return f"HANDOFF:researcher:{topic}"

@tool
def handoff_to_writer(content: str) -> str:
    """Hand off to writer for content creation."""
    return f"HANDOFF:writer:{content}"

coordinator = Agent(
    tools=[handoff_to_researcher, handoff_to_writer],
    system_prompt="Coordinate between researcher and writer."
)
```

---

## Multi-Agent Patterns

### Pipeline Pattern

Sequential processing through specialized agents:

```
Input → Researcher → Analyzer → Writer → Reviewer → Output
```

```python
swarm = Swarm(
    agents=[researcher, analyzer, writer, reviewer],
    entry_point=researcher,
    max_handoffs=4,  # One per transition
)
```

### Hub-and-Spoke Pattern

Coordinator delegates to specialists:

```
              ┌─→ Specialist A ─┐
Input → Hub ─┼─→ Specialist B ─┼─→ Hub → Output
              └─→ Specialist C ─┘
```

```python
hub = Agent(
    name="hub",
    system_prompt="""You are a coordinator.
    Delegate to specialists as needed.
    Collect and synthesize their outputs."""
)
```

### Peer Review Pattern

Agents review each other's work:

```python
agent_a = Agent(
    name="agent_a",
    system_prompt="Create solution. Have agent_b review."
)

agent_b = Agent(
    name="agent_b",
    system_prompt="Review agent_a's work. Suggest improvements."
)
```

---

## Swarm Result

```python
result = swarm.run("Task description")

# Result properties
result.status        # "completed" | "failed"
result.node_history  # List of agent names in execution order
result.output        # Final output from last agent
```

---

## Safety Features

### Ping-Pong Detection

Prevent infinite loops between agents:

```python
swarm = Swarm(
    agents=[...],
    repetitive_handoff_detection_window=8,   # Check last 8 handoffs
    repetitive_handoff_min_unique_agents=3,  # Require 3+ unique agents
)
```

### Timeouts

```python
swarm = Swarm(
    agents=[...],
    execution_timeout=300.0,  # 5 min total
    node_timeout=60.0,        # 1 min per agent
)
```

### Iteration Limits

```python
swarm = Swarm(
    agents=[...],
    max_handoffs=10,    # Max agent switches
    max_iterations=15,  # Max total model calls
)
```

---

## Best Practices

1. **Clear Roles**: Each agent should have a distinct responsibility
2. **Explicit Handoffs**: Describe when/how to hand off in system prompts
3. **Reasonable Limits**: Set timeouts and iteration limits
4. **Monitor History**: Check node_history to debug flow issues
5. **Entry Point**: Choose the most logical starting agent
6. **Termination**: Ensure at least one agent can "finish" the task
