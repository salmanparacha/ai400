# Production Patterns Reference

## Guardrails

### Bedrock Native Guardrails

```python
from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-20250514-v1:0",
    guardrail_id="your-guardrail-id",
    guardrail_version="1",
    guardrail_trace="enabled",
    guardrail_stream_processing_mode="sync",
    guardrail_redact_input=True,
    guardrail_redact_output=False,
)

agent = Agent(model=model)
```

### Guardrail Options

| Option | Values | Description |
|--------|--------|-------------|
| `guardrail_trace` | `"enabled"`, `"disabled"`, `"enabled_full"` | Trace detail level |
| `guardrail_stream_processing_mode` | `"sync"`, `"async"` | Processing mode |
| `guardrail_redact_input` | `True`/`False` | Redact blocked input |
| `guardrail_redact_output` | `True`/`False` | Redact blocked output |

---

## Session Management

### Local File Persistence

```python
from strands import Agent
from strands.session.file_session_manager import FileSessionManager

session_manager = FileSessionManager(session_id="user-123")
agent = Agent(session_manager=session_manager)

# Conversations persist automatically
agent("My name is Alice")
# Later session...
agent("What's my name?")  # Remembers Alice
```

### AWS AgentCore Memory

```python
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

config = AgentCoreMemoryConfig(
    memory_id="your-memory-id",
    session_id="session-123",
    actor_id="user-456"
)

session_manager = AgentCoreMemorySessionManager(
    agentcore_memory_config=config,
    region_name="us-east-1"
)

agent = Agent(
    system_prompt="You are a helpful assistant.",
    session_manager=session_manager,
)
```

---

## Observability

### Basic Telemetry

```python
from strands import Agent
from strands.telemetry import StrandsTelemetry

telemetry = StrandsTelemetry()
telemetry.setup_otlp_exporter()      # Send to OTLP endpoint
telemetry.setup_console_exporter()   # Print to console
telemetry.setup_meter(
    enable_console_exporter=True,
    enable_otlp_exporter=True
)

agent = Agent(system_prompt="You are helpful.")
response = agent("Hello")
```

### AWS ADOT Configuration

```bash
# Enable agent observability
export AGENT_OBSERVABILITY_ENABLED="true"

# ADOT configuration
export OTEL_PYTHON_DISTRO="aws_distro"
export OTEL_PYTHON_CONFIGURATOR="aws_configurator"
export OTEL_LOG_LEVEL="info"

# Exporters
export OTEL_METRICS_EXPORTER="awsemf"
export OTEL_TRACES_EXPORTER="otlp"
export OTEL_LOGS_EXPORTER="otlp"
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"

# Service configuration
export OTEL_RESOURCE_ATTRIBUTES="service.name=my-agent,aws.log.group.names=/aws/agents/my-agent"

# Endpoints
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://xray.us-east-1.amazonaws.com/v1/traces"
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://logs.us-east-1.amazonaws.com/v1/logs"

# Capture content
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT="true"
```

Run with instrumentation:

```bash
opentelemetry-instrument python my_agent.py
```

---

## Error Handling

### Agent-Level

```python
from strands import Agent

agent = Agent(tools=[...])

try:
    response = agent("User query")
    print(response.message)
except Exception as e:
    print(f"Agent error: {e}")
    # Fallback behavior
```

### Tool-Level

```python
from strands import tool

@tool
def robust_tool(input: str) -> str:
    """Process input safely."""
    try:
        result = process(input)
        return result
    except ValueError as e:
        return f"Invalid input: {e}"
    except TimeoutError:
        return "Operation timed out, please retry"
    except Exception as e:
        return f"Unexpected error: {e}"
```

### Hook-Based Error Handling

```python
from strands.hooks import HookProvider, HookRegistry, AfterInvocationEvent

class ErrorHandler(HookProvider):
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterInvocationEvent, self.handle_errors)

    def handle_errors(self, event: AfterInvocationEvent) -> None:
        if hasattr(event, 'error') and event.error:
            # Log error, send alert, etc.
            log_error(event.error)
```

---

## Structured Output in Production

```python
from pydantic import BaseModel, Field, validator
from strands import Agent

class APIResponse(BaseModel):
    status: str = Field(description="success or error")
    data: dict = Field(description="Response data")
    message: str = Field(description="Human-readable message")

    @validator('status')
    def validate_status(cls, v):
        if v not in ('success', 'error'):
            raise ValueError('Status must be success or error')
        return v

agent = Agent()
result = agent.structured_output(
    APIResponse,
    "Process this user request..."
)

# Type-safe access
print(result.status)
print(result.data)
```

---

## MCP Integration

### Connect to MCP Server

```python
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp.mcp_client import MCPClient

def create_transport():
    return streamablehttp_client("http://localhost:8000/mcp/")

mcp_client = MCPClient(create_transport)

with mcp_client:
    tools = mcp_client.list_tools_sync()
    agent = Agent(
        system_prompt="Use available tools to help users.",
        tools=tools
    )
    response = agent("User request")
```

### Create MCP Server

```python
from mcp.server import FastMCP

mcp = FastMCP("My Server")

@mcp.tool(description="Add two numbers")
def add(x: int, y: int) -> int:
    return x + y

@mcp.tool(description="Multiply two numbers")
def multiply(x: int, y: int) -> int:
    return x * y

# Run with SSE transport
mcp.run(transport="sse")

# Or streamable HTTP
mcp.run(transport="streamable-http")
```

---

## Configuration from Dict

```python
from strands.experimental import config_to_agent

agent = config_to_agent({
    "model": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "prompt": "You are a helpful assistant.",
})
```

---

## Production Checklist

### Security
- [ ] Guardrails configured for content filtering
- [ ] Input validation in tools
- [ ] No secrets in system prompts
- [ ] Rate limiting on tool calls

### Reliability
- [ ] Error handling at all levels
- [ ] Timeouts configured
- [ ] Retry logic for transient failures
- [ ] Session persistence for long conversations

### Observability
- [ ] Telemetry enabled
- [ ] Structured logging
- [ ] Metrics collection
- [ ] Tracing for debugging

### Performance
- [ ] Appropriate model selection
- [ ] Token limits configured
- [ ] Async tools for I/O operations
- [ ] Caching where appropriate

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `AWS_REGION` | AWS region for Bedrock |
| `ANTHROPIC_API_KEY` | Anthropic direct API |
| `OPENAI_API_KEY` | OpenAI API |
| `AGENT_OBSERVABILITY_ENABLED` | Enable telemetry |
| `OTEL_*` | OpenTelemetry configuration |
