# Callback Handlers

This reference covers using callback handlers for monitoring, debugging, and logging Strands agent execution.

## Table of Contents

- [What are Callback Handlers](#what-are-callback-handlers)
- [Built-in Handlers](#built-in-handlers)
- [Custom Handlers](#custom-handlers)
- [Monitoring Tool Usage](#monitoring-tool-usage)
- [Logging Patterns](#logging-patterns)
- [Production Handlers](#production-handlers)

## What are Callback Handlers

Callback handlers are functions that receive real-time updates during agent execution. They allow you to:
- Monitor agent responses as they stream
- Track which tools the agent uses
- Log agent behavior for debugging
- Implement custom UI updates
- Collect metrics and analytics

## Built-in Handlers

### PrintingCallbackHandler

The default handler that prints agent output and tool usage:

```python
from strands import Agent
from strands.handlers.callback_handler import PrintingCallbackHandler

agent = Agent(callback_handler=PrintingCallbackHandler())

# This will print:
# - Streamed agent responses
# - Tool usage notifications
agent("What is 42 * 17?")
```

### No Handler (Silent Mode)

Disable output by setting `callback_handler=None`:

```python
from strands import Agent

# Silent agent - no output during execution
agent = Agent(callback_handler=None)

# Only get final result
result = agent("Calculate 100 + 200")
print(result)  # Print only final answer
```

## Custom Handlers

### Basic Custom Handler

```python
from strands import Agent
from strands_tools import calculator

def custom_callback_handler(**kwargs):
    """Basic callback handler to monitor agent execution."""
    # Handle streamed text data
    if "data" in kwargs:
        print(f"MODEL OUTPUT: {kwargs['data']}")

    # Handle tool usage
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(f"\nUSING TOOL: {kwargs['current_tool_use']['name']}")

agent = Agent(
    tools=[calculator],
    callback_handler=custom_callback_handler
)

agent("Calculate 2+2")
```

**Callback receives these kwargs:**
- `data`: Streamed text chunks from the model
- `current_tool_use`: Dictionary with tool information when agent uses a tool

### Handler with Tool Tracking

```python
tool_use_ids = []

def callback_handler(**kwargs):
    """Track unique tool usage."""
    if "data" in kwargs:
        # Log streamed text chunks
        print(kwargs["data"], end="")

    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        # Only log each tool use once (avoid duplicates)
        if tool["toolUseId"] not in tool_use_ids:
            print(f"\n[Using tool: {tool.get('name')}]")
            tool_use_ids.append(tool["toolUseId"])

from strands_tools import shell

agent = Agent(
    tools=[shell],
    callback_handler=callback_handler
)

result = agent("What operating system am I using?")
```

### Debug Handler

Inspect all callback data:

```python
def debugger_callback_handler(**kwargs):
    """Print all callback data for debugging."""
    print("=== CALLBACK DATA ===")
    print(kwargs)
    print("====================\n")

from strands_tools import calculator

agent = Agent(
    tools=[calculator],
    callback_handler=debugger_callback_handler
)

agent("What is 922 + 5321")
```

## Monitoring Tool Usage

### Counting Tool Calls

```python
tool_counts = {}

def tool_counter_handler(**kwargs):
    """Count how many times each tool is used."""
    if "data" in kwargs:
        print(kwargs["data"], end="")

    elif "current_tool_use" in kwargs:
        tool_name = kwargs["current_tool_use"].get("name")
        if tool_name:
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            print(f"\n[Tool: {tool_name} (call #{tool_counts[tool_name]})]")

agent = Agent(
    tools=[calculator, current_time],
    callback_handler=tool_counter_handler
)

agent("What time is it? Also calculate 10 + 20")

print(f"\nTool usage summary: {tool_counts}")
# Output: {"current_time": 1, "calculator": 1}
```

### Tool Input/Output Tracking

```python
def tool_tracker_handler(**kwargs):
    """Track tool inputs and outputs."""
    if "data" in kwargs:
        print(kwargs["data"], end="")

    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        print(f"\n[Tool: {tool.get('name')}]")
        print(f"  Input: {tool.get('input', {})}")
        # Note: Output is not available in this callback
        # It will appear in subsequent "data" callbacks

agent = Agent(
    tools=[calculator],
    callback_handler=tool_tracker_handler
)

agent("Calculate 15 * 8")
```

## Logging Patterns

### Basic Logging Handler

```python
import logging

logger = logging.getLogger("strands_agent")
logger.setLevel(logging.INFO)

# Add file handler
fh = logging.FileHandler("agent.log")
logger.addHandler(fh)

# Add console handler
ch = logging.StreamHandler()
logger.addHandler(ch)

tool_use_ids = []

def logging_callback_handler(**kwargs):
    """Log agent activity to file and console."""
    if "data" in kwargs:
        logger.info(kwargs["data"], end="")

    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        if tool["toolUseId"] not in tool_use_ids:
            logger.info(f"\n[Using tool: {tool.get('name')}]")
            tool_use_ids.append(tool["toolUseId"])

from strands_tools import shell

agent = Agent(
    tools=[shell],
    callback_handler=logging_callback_handler
)

result = agent("What operating system am I using?")
print(result.message)
```

### Structured Logging

```python
import logging
import json
from datetime import datetime

logger = logging.getLogger("strands_agent")

def structured_logging_handler(**kwargs):
    """Log structured data for analysis."""
    timestamp = datetime.utcnow().isoformat()

    if "data" in kwargs:
        log_entry = {
            "timestamp": timestamp,
            "type": "model_output",
            "data": kwargs["data"]
        }
        logger.info(json.dumps(log_entry))

    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        log_entry = {
            "timestamp": timestamp,
            "type": "tool_use",
            "tool_name": tool.get("name"),
            "tool_id": tool.get("toolUseId"),
            "tool_input": tool.get("input", {})
        }
        logger.info(json.dumps(log_entry))

agent = Agent(
    tools=[calculator],
    callback_handler=structured_logging_handler
)
```

### Multi-Level Logging

```python
import logging

# Set up loggers for different severity levels
info_logger = logging.getLogger("agent.info")
debug_logger = logging.getLogger("agent.debug")
error_logger = logging.getLogger("agent.error")

def multi_level_handler(**kwargs):
    """Use different log levels for different events."""
    if "data" in kwargs:
        # Normal output at INFO level
        info_logger.info(kwargs["data"])

    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        # Tool usage at DEBUG level
        debug_logger.debug(f"Tool used: {tool.get('name')} with input: {tool.get('input')}")

    # Could add error handling here
    # elif "error" in kwargs:
    #     error_logger.error(kwargs["error"])

agent = Agent(
    tools=[calculator],
    callback_handler=multi_level_handler
)
```

## Production Handlers

### Metrics Collection Handler

```python
from datetime import datetime
import time

class MetricsCollector:
    """Collect agent execution metrics."""
    def __init__(self):
        self.start_time = None
        self.tool_calls = []
        self.response_length = 0

    def __call__(self, **kwargs):
        if self.start_time is None:
            self.start_time = time.time()

        if "data" in kwargs:
            self.response_length += len(kwargs["data"])

        elif "current_tool_use" in kwargs:
            tool = kwargs["current_tool_use"]
            self.tool_calls.append({
                "name": tool.get("name"),
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_metrics(self):
        """Return collected metrics."""
        return {
            "execution_time": time.time() - self.start_time if self.start_time else 0,
            "tool_calls": len(self.tool_calls),
            "tools_used": self.tool_calls,
            "response_length": self.response_length
        }

# Use the metrics collector
metrics = MetricsCollector()

agent = Agent(
    tools=[calculator, current_time],
    callback_handler=metrics
)

result = agent("What time is it? Calculate 10 + 20")

print(f"\nMetrics: {metrics.get_metrics()}")
```

### Custom UI Handler

```python
class UIHandler:
    """Handler for updating custom UI."""
    def __init__(self, ui_update_function):
        self.ui_update = ui_update_function
        self.buffer = ""

    def __call__(self, **kwargs):
        if "data" in kwargs:
            # Accumulate text
            self.buffer += kwargs["data"]
            # Update UI with current buffer
            self.ui_update({"type": "text", "content": self.buffer})

        elif "current_tool_use" in kwargs:
            tool = kwargs["current_tool_use"]
            # Show tool usage in UI
            self.ui_update({
                "type": "tool",
                "name": tool.get("name"),
                "input": tool.get("input")
            })

def update_my_ui(data):
    """Mock UI update function."""
    print(f"UI Update: {data}")

ui_handler = UIHandler(update_my_ui)

agent = Agent(
    tools=[calculator],
    callback_handler=ui_handler
)

agent("Calculate 5 * 5")
```

### Combined Handler

Combine multiple handlers:

```python
def combined_handler(**kwargs):
    """Run multiple handlers."""
    # Log to file
    logging_handler(**kwargs)

    # Collect metrics
    metrics_handler(**kwargs)

    # Update UI
    ui_handler(**kwargs)

agent = Agent(
    tools=[calculator],
    callback_handler=combined_handler
)
```

### Rate Limiting Handler

```python
import time

class RateLimitedHandler:
    """Handler that rate-limits output updates."""
    def __init__(self, min_interval=0.1):
        self.last_update = 0
        self.min_interval = min_interval
        self.buffer = ""

    def __call__(self, **kwargs):
        current_time = time.time()

        if "data" in kwargs:
            self.buffer += kwargs["data"]

            # Only update if enough time has passed
            if current_time - self.last_update >= self.min_interval:
                print(self.buffer, end="")
                self.buffer = ""
                self.last_update = current_time

        elif "current_tool_use" in kwargs:
            # Always show tool usage immediately
            print(f"\n[Using: {kwargs['current_tool_use'].get('name')}]")
            self.last_update = current_time

    def flush(self):
        """Flush any remaining buffered content."""
        if self.buffer:
            print(self.buffer, end="")
            self.buffer = ""

handler = RateLimitedHandler(min_interval=0.5)

agent = Agent(
    tools=[calculator],
    callback_handler=handler
)

result = agent("Calculate 100 * 200")
handler.flush()  # Ensure all output is shown
```
