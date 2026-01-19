# Hooks & Lifecycle Reference

## Available Events

| Event | When Triggered | Use Case |
|-------|----------------|----------|
| `AgentInitializedEvent` | After agent constructor completes | Setup, validation |
| `BeforeInvocationEvent` | Start of agent request | Logging, auth |
| `AfterInvocationEvent` | End of agent request | Cleanup, metrics |
| `MessageAddedEvent` | Message added to history | Monitoring, filtering |
| `BeforeModelCallEvent` | Before model inference | Token counting |
| `AfterModelCallEvent` | After model inference | Response logging |
| `BeforeToolCallEvent` | Before tool execution | Validation, interception |
| `AfterToolCallEvent` | After tool execution | Result modification |

---

## Basic Hook Implementation

```python
from strands import Agent
from strands.hooks import (
    HookProvider,
    HookRegistry,
    BeforeInvocationEvent,
    AfterInvocationEvent,
)

class LoggingHook(HookProvider):
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.on_start)
        registry.add_callback(AfterInvocationEvent, self.on_end)

    def on_start(self, event: BeforeInvocationEvent) -> None:
        print(f"Request started: {event.agent.name}")

    def on_end(self, event: AfterInvocationEvent) -> None:
        print(f"Request completed: {event.agent.name}")

# Use hook
agent = Agent(hooks=[LoggingHook()])
```

---

## Adding Hooks After Creation

```python
agent = Agent()

# Add hook provider
agent.hooks.add_hook(LoggingHook())

# Or add individual callback
def my_callback(event: BeforeInvocationEvent) -> None:
    print("Custom callback triggered")

agent.hooks.add_callback(BeforeInvocationEvent, my_callback)
```

---

## Modifiable Event Properties

### AfterModelCallEvent

```python
class RetryHook(HookProvider):
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterModelCallEvent, self.maybe_retry)

    def maybe_retry(self, event: AfterModelCallEvent) -> None:
        if should_retry(event):
            event.retry = True  # Request model retry
```

### BeforeToolCallEvent

```python
class ToolInterceptHook(HookProvider):
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.intercept)

    def intercept(self, event: BeforeToolCallEvent) -> None:
        # Cancel tool execution
        event.cancel_tool = True

        # Or replace tool
        event.selected_tool = alternative_tool

        # Or modify parameters
        event.tool_use["input"]["param"] = "new_value"
```

### AfterToolCallEvent

```python
class ResultModifyHook(HookProvider):
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterToolCallEvent, self.modify)

    def modify(self, event: AfterToolCallEvent) -> None:
        # Modify tool result before it's used
        event.result = sanitize(event.result)
```

---

## Common Hook Patterns

### Request Logging

```python
import time
from strands.hooks import *

class MetricsHook(HookProvider):
    def __init__(self):
        self.start_time = None

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.start_timer)
        registry.add_callback(AfterInvocationEvent, self.log_metrics)

    def start_timer(self, event: BeforeInvocationEvent) -> None:
        self.start_time = time.time()

    def log_metrics(self, event: AfterInvocationEvent) -> None:
        duration = time.time() - self.start_time
        print(f"Request took {duration:.2f}s")
```

### Tool Usage Tracking

```python
class ToolTracker(HookProvider):
    def __init__(self):
        self.tool_calls = []

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.track)

    def track(self, event: BeforeToolCallEvent) -> None:
        self.tool_calls.append({
            "tool": event.tool_use["name"],
            "input": event.tool_use.get("input", {}),
        })
```

### Input Validation

```python
class ValidationHook(HookProvider):
    def __init__(self, blocked_words: list):
        self.blocked_words = blocked_words

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(MessageAddedEvent, self.validate)

    def validate(self, event: MessageAddedEvent) -> None:
        if event.message.get("role") == "user":
            content = str(event.message.get("content", ""))
            for word in self.blocked_words:
                if word.lower() in content.lower():
                    raise ValueError(f"Blocked content detected")
```

### Tool Rate Limiting

```python
class RateLimitHook(HookProvider):
    def __init__(self, max_calls: int = 10):
        self.max_calls = max_calls
        self.call_count = 0

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.check_limit)

    def check_limit(self, event: BeforeToolCallEvent) -> None:
        self.call_count += 1
        if self.call_count > self.max_calls:
            event.cancel_tool = True
            # Tool will receive cancellation message
```

---

## Shadow-Mode Guardrails Hook

Check content without blocking:

```python
import boto3
from strands.hooks import *

class ShadowGuardrailHook(HookProvider):
    def __init__(self, guardrail_id: str, version: str):
        self.guardrail_id = guardrail_id
        self.version = version
        self.client = boto3.client("bedrock-runtime")

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(MessageAddedEvent, self.check_input)
        registry.add_callback(AfterInvocationEvent, self.check_output)

    def check_input(self, event: MessageAddedEvent) -> None:
        if event.message.get("role") == "user":
            content = self._extract_text(event.message)
            self._evaluate(content, "INPUT")

    def check_output(self, event: AfterInvocationEvent) -> None:
        if event.agent.messages:
            last = event.agent.messages[-1]
            if last.get("role") == "assistant":
                content = self._extract_text(last)
                self._evaluate(content, "OUTPUT")

    def _extract_text(self, message: dict) -> str:
        return "".join(
            block.get("text", "")
            for block in message.get("content", [])
        )

    def _evaluate(self, content: str, source: str) -> None:
        response = self.client.apply_guardrail(
            guardrailIdentifier=self.guardrail_id,
            guardrailVersion=self.version,
            source=source,
            content=[{"text": {"text": content}}]
        )
        if response.get("action") == "GUARDRAIL_INTERVENED":
            print(f"[GUARDRAIL] Would block {source}: {content[:50]}...")
```

---

## Callback Ordering

Before/After event pairs use reverse ordering for cleanup:

```
BeforeInvocationEvent callbacks: A → B → C
AfterInvocationEvent callbacks:  C → B → A
```

This ensures proper cleanup semantics (last setup, first cleanup).

---

## Event Properties Reference

### BeforeInvocationEvent

- `agent`: The Agent instance
- `input`: User input message

### AfterInvocationEvent

- `agent`: The Agent instance
- `result`: Final response

### MessageAddedEvent

- `agent`: The Agent instance
- `message`: The message dict with `role` and `content`

### BeforeToolCallEvent

- `agent`: The Agent instance
- `tool_use`: Tool call details (name, input)
- `selected_tool`: Tool to execute (modifiable)
- `cancel_tool`: Set True to cancel (modifiable)

### AfterToolCallEvent

- `agent`: The Agent instance
- `tool_use`: Tool call details
- `result`: Tool result (modifiable)

### BeforeModelCallEvent

- `agent`: The Agent instance
- `messages`: Message history

### AfterModelCallEvent

- `agent`: The Agent instance
- `response`: Model response
- `retry`: Set True to retry (modifiable)
