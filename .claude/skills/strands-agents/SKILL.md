---
name: strands-agents
description: |
  Build AI agents with AWS Strands SDK from hello world to production systems.
  This skill should be used when creating agents, multi-agent systems, custom tools,
  or integrating with model providers (Bedrock, Anthropic, OpenAI). Covers agent
  configuration, structured outputs, session management, guardrails, and observability.
---

# Strands Agents Skill

Build AI agents from minimal examples to production-ready systems using AWS Strands SDK.

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing patterns, model provider in use, tool conventions |
| **Conversation** | User's specific agent requirements, constraints |
| **Skill References** | Patterns from `references/` (model configs, tools, multi-agent) |
| **User Guidelines** | Project conventions, AWS region, security requirements |

### Required Clarifications

Before building, clarify with user:

1. **Model Provider** - Which provider? (Bedrock default, Anthropic, OpenAI)
2. **Tools Needed** - What capabilities? (built-in strands_tools, custom, MCP)
3. **Complexity** - Single agent or multi-agent swarm?

### Optional Clarifications

4. **Persistence** - Need conversation memory? (FileSessionManager, AgentCore)
5. **Production** - Need guardrails, telemetry, hooks?
6. **Structured Output** - Need typed responses? (Pydantic models)

---

## What This Skill Does NOT Do

- Deploy agents to AWS/cloud (use CDK, SAM, or Terraform)
- Create or manage Bedrock guardrails (use AWS Console or CLI)
- Manage AWS credentials or IAM roles
- Create MCP servers (only shows integration patterns)
- Handle billing or cost optimization

---

## Official Documentation

| Resource | URL |
|----------|-----|
| Strands SDK GitHub | https://github.com/strands-agents/sdk-python |
| Strands Tools | https://github.com/strands-agents/tools |
| AWS Blog Announcement | https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/ |
| AWS Bedrock Models | https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html |
| PyPI strands-agents | https://pypi.org/project/strands-agents/ |
| PyPI strands-agents-tools | https://pypi.org/project/strands-agents-tools/ |

---

## Quick Start Templates

### Minimal Agent

```python
from strands import Agent

agent = Agent()
response = agent("Hello, what can you help me with?")
print(response)
```

### Agent with Tools

```python
from strands import Agent
from strands_tools import calculator, file_read, shell

agent = Agent(tools=[calculator, file_read, shell])
agent("What is 42 ^ 9?")
```

### Agent with Custom Tool

```python
from strands import Agent, tool

@tool
def weather(city: str) -> str:
    """Get weather for a city.

    Args:
        city: City name to get weather for
    """
    return f"Weather for {city}: Sunny, 72F"

agent = Agent(tools=[weather])
agent("What's the weather in Seattle?")
```

---

## Installation

```bash
# Recommended: Install SDK + tools together
pip install strands-agents strands-agents-tools

# Or install separately
pip install strands-agents              # Core SDK only
pip install strands-agents-tools        # 40+ built-in tools

# With specific model providers
pip install 'strands-agents[anthropic]'  # Anthropic direct API
pip install 'strands-agents[openai]'     # OpenAI
pip install 'strands-agents[all]'        # All providers
```

---

## Core Patterns

### 1. Agent Configuration

```python
from strands import Agent

agent = Agent(
    system_prompt="You are a helpful assistant specialized in X.",
    tools=[...],              # List of tool functions
    model=model_instance,     # Model provider (optional, defaults to Bedrock)
    callback_handler=fn,      # Stream handling (optional)
    session_manager=mgr,      # Conversation persistence (optional)
    hooks=[...],              # Lifecycle hooks (optional)
)

# Invoke
response = agent("User message")
print(response.message)  # Final response text
```

### 2. Model Providers

```python
# AWS Bedrock - Claude (default)
from strands.models.bedrock import BedrockModel
model = BedrockModel(model_id="anthropic.claude-sonnet-4-20250514-v1:0")

# AWS Bedrock - Amazon Nova
model = BedrockModel(model_id="amazon.nova-pro-v1:0")  # Balanced
model = BedrockModel(model_id="amazon.nova-lite-v1:0")  # Fast/cheap
model = BedrockModel(model_id="amazon.nova-premier-v1:0")  # Most capable
model = BedrockModel(model_id="amazon.nova-2-lite-v1:0")  # Extended thinking

# Anthropic Direct
from strands.models.anthropic import AnthropicModel
model = AnthropicModel(
    client_args={"api_key": "..."},
    model_id="claude-sonnet-4-20250514",
    max_tokens=1024
)

# OpenAI
from strands.models.openai import OpenAIModel
model = OpenAIModel(
    client_args={"api_key": "..."},
    model_id="gpt-4o"
)

agent = Agent(model=model)
```

See `references/model-providers.md` for full configuration options including all Nova models.

### 3. Custom Tools

```python
from strands import tool

@tool
def my_tool(param1: str, param2: int = 10) -> str:
    """Tool description shown to the model.

    Args:
        param1: Description of param1
        param2: Description of param2
    """
    return f"Result: {param1}, {param2}"

# Async tools
@tool
async def async_tool(query: str) -> str:
    """Async tools run concurrently."""
    result = await some_async_operation(query)
    return result
```

See `references/custom-tools.md` for patterns and best practices.

### 4. Structured Output

```python
from pydantic import BaseModel, Field
from strands import Agent

class PersonInfo(BaseModel):
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years")
    occupation: str = Field(description="Job title")

agent = Agent()
result = agent.structured_output(
    PersonInfo,
    "John Smith is a 30-year-old software engineer"
)

print(result.name)       # "John Smith"
print(result.age)        # 30
print(result.occupation) # "software engineer"
```

### 5. Session Management

```python
from strands import Agent
from strands.session.file_session_manager import FileSessionManager

# Local file persistence
session_manager = FileSessionManager(session_id="user-123")
agent = Agent(session_manager=session_manager)

# Conversations auto-persist
agent("My name is Alice")
# Later...
agent("What's my name?")  # Remembers "Alice"
```

### 6. Callback Handlers (Streaming)

```python
from strands import Agent

def callback_handler(**kwargs):
    if "data" in kwargs:
        print(kwargs["data"], end="")  # Stream text
    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        print(f"\n[Using: {tool.get('name')}]")

agent = Agent(callback_handler=callback_handler)
agent("Explain quantum computing")
```

---

## Multi-Agent Systems

### Swarm Tool (Simple)

```python
from strands import Agent
from strands_tools import swarm

agent = Agent(
    tools=[swarm],
    system_prompt="Create a swarm of agents to solve complex queries."
)

agent("Research and summarize quantum computing advances")
```

### Explicit Swarm (Advanced)

```python
from strands import Agent
from strands.multiagent import Swarm

researcher = Agent(
    name="researcher",
    system_prompt="You research topics and gather facts."
)

writer = Agent(
    name="writer",
    system_prompt="You write clear summaries from research."
)

swarm = Swarm(
    agents=[researcher, writer],
    entry_point=researcher,
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,
    node_timeout=300.0,
)

result = swarm.run("Explain machine learning")
print(result.status)  # "completed"
```

See `references/multi-agent.md` for orchestration patterns.

---

## Production Patterns

### Guardrails (Bedrock)

```python
from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-20250514-v1:0",
    guardrail_id="your-guardrail-id",
    guardrail_version="1",
    guardrail_trace="enabled",
)

agent = Agent(model=model)
```

### Lifecycle Hooks

```python
from strands import Agent
from strands.hooks import (
    HookProvider, HookRegistry,
    BeforeInvocationEvent, AfterInvocationEvent,
    BeforeToolCallEvent, AfterToolCallEvent
)

class LoggingHook(HookProvider):
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.on_start)
        registry.add_callback(AfterInvocationEvent, self.on_end)
        registry.add_callback(BeforeToolCallEvent, self.on_tool)

    def on_start(self, event: BeforeInvocationEvent):
        print(f"Request started: {event.agent.name}")

    def on_end(self, event: AfterInvocationEvent):
        print(f"Request completed: {event.agent.name}")

    def on_tool(self, event: BeforeToolCallEvent):
        print(f"Tool called: {event.tool_use['name']}")

agent = Agent(hooks=[LoggingHook()])
```

### Observability

```python
from strands import Agent
from strands.telemetry import StrandsTelemetry

telemetry = StrandsTelemetry()
telemetry.setup_otlp_exporter()  # Send to OTLP endpoint
telemetry.setup_console_exporter()  # Also print to console

agent = Agent(system_prompt="You are helpful.")
response = agent("Hello")
```

See `references/production-patterns.md` for complete setup.

---

## MCP Integration

```python
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp.mcp_client import MCPClient

def create_transport():
    return streamablehttp_client("http://localhost:8000/mcp/")

mcp_client = MCPClient(create_transport)

with mcp_client:
    tools = mcp_client.list_tools_sync()
    agent = Agent(tools=tools)
    response = agent("Use the MCP tools to help me")
```

---

## Decision Tree

```
What type of agent?
├── Single agent, simple task
│   └── Use basic Agent() with tools
├── Single agent, needs memory
│   └── Add FileSessionManager or AgentCoreMemorySessionManager
├── Multiple agents collaborate
│   └── Use Swarm with defined agent roles
├── Need structured data extraction
│   └── Use agent.structured_output() with Pydantic
├── Production deployment
│   └── Add guardrails + hooks + telemetry
└── External tool servers
    └── Use MCPClient integration
```

---

## Project Templates

Start new projects from templates in `assets/`:

| Template | Description | Use When |
|----------|-------------|----------|
| `assets/minimal/` | Hello world agent | Learning basics |
| `assets/custom-tools/` | Agent with custom tools | Building tool-based agents |
| `assets/multi-agent/` | Swarm with multiple agents | Complex workflows |
| `assets/production/` | Full production setup | Deploying to production |

Use `scripts/create_project.py` to scaffold:
```bash
python scripts/create_project.py my-agent --template production
```

---

## Reference Files

| File | Content |
|------|---------|
| `references/model-providers.md` | All model configs (Bedrock Claude, Nova, Anthropic, OpenAI) |
| `references/custom-tools.md` | Tool patterns, async tools, validation |
| `references/multi-agent.md` | Swarm configuration, handoff patterns |
| `references/hooks-lifecycle.md` | All events, hook patterns, modifications |
| `references/production-patterns.md` | Guardrails, observability, session management |

---

## Common Patterns

> **Note**: All examples below assume `from strands import Agent, tool` is imported.

### Error Handling in Tools

```python
from strands import tool

@tool
def safe_operation(input: str) -> str:
    """Safely process input."""
    try:
        result = process(input)
        return result
    except ValueError as e:
        return f"Error: {str(e)}"
```

### Tool with Dependencies

```python
import httpx
from strands import tool

@tool
def fetch_data(url: str) -> str:
    """Fetch data from URL."""
    response = httpx.get(url)
    return response.text
```

### Conditional Tool Selection

```python
from strands import Agent, tool

@tool
def database_query(sql: str) -> str:
    """Query the database. Use for data retrieval."""
    # Implementation
    pass

@tool
def api_call(endpoint: str) -> str:
    """Call external API. Use for real-time data."""
    # Implementation
    pass

agent = Agent(
    tools=[database_query, api_call],
    system_prompt="Use database for historical data, API for real-time."
)
```
