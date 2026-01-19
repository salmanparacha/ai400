# Custom Tools Reference

## Basic Tool Definition

```python
from strands import tool

@tool
def my_tool(param1: str, param2: int = 10) -> str:
    """Short description shown to model.

    Args:
        param1: Description of first parameter
        param2: Description with default value
    """
    return f"Result: {param1}, {param2}"
```

### Requirements

1. Use `@tool` decorator
2. Include docstring with description
3. Document Args in Google style
4. Use type hints for all parameters
5. Return string or serializable type

---

## Tool with Custom Name/Description

```python
@tool(name="get_weather", description="Retrieves weather forecast for a city")
def weather_forecast(city: str, days: int = 3) -> str:
    """Implementation function.

    Args:
        city: City name
        days: Forecast days
    """
    return f"Weather for {city}: Sunny"
```

---

## Async Tools

Async tools run concurrently when multiple are invoked:

```python
import asyncio
from strands import tool

@tool
async def call_api(endpoint: str) -> str:
    """Call external API asynchronously.

    Args:
        endpoint: API endpoint URL
    """
    await asyncio.sleep(1)  # Simulated API call
    return f"Response from {endpoint}"
```

### Using Async Agent

```python
async def main():
    agent = Agent(tools=[call_api])
    await agent.invoke_async("Call the user API")

asyncio.run(main())
```

---

## Tool Return Types

### String (Recommended)

```python
@tool
def simple_tool(input: str) -> str:
    return "Result as string"
```

### Dict (Structured)

```python
@tool
def structured_tool(input: str) -> dict:
    return {"status": "success", "data": [...]}
```

### Error Handling

```python
@tool
def safe_tool(input: str) -> str:
    """Process input safely."""
    try:
        result = risky_operation(input)
        return result
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

---

## Parameter Types

### Required Parameters

```python
@tool
def required_params(name: str, age: int) -> str:
    """All parameters required."""
    return f"{name} is {age}"
```

### Optional Parameters

```python
@tool
def optional_params(name: str, title: str = "User") -> str:
    """Title is optional with default."""
    return f"{title} {name}"
```

### Complex Types

```python
from typing import List, Optional

@tool
def complex_params(
    items: List[str],
    limit: Optional[int] = None
) -> str:
    """Handle lists and optionals."""
    result = items[:limit] if limit else items
    return str(result)
```

---

## Tool Categories

### Data Retrieval

```python
import httpx
from strands import tool

@tool
def fetch_url(url: str) -> str:
    """Fetch content from a URL.

    Args:
        url: The URL to fetch
    """
    response = httpx.get(url, timeout=30)
    return response.text[:5000]  # Limit response size
```

### Computation

```python
@tool
def calculate(expression: str) -> str:
    """Evaluate mathematical expression.

    Args:
        expression: Math expression like "2 + 2"
    """
    # Safe evaluation
    allowed = set("0123456789+-*/.()")
    if not all(c in allowed for c in expression.replace(" ", "")):
        return "Invalid expression"
    return str(eval(expression))
```

### File Operations

```python
from pathlib import Path
from strands import tool

@tool
def read_file(filepath: str) -> str:
    """Read content from a file.

    Args:
        filepath: Path to the file
    """
    path = Path(filepath)
    if not path.exists():
        return f"File not found: {filepath}"
    return path.read_text()[:10000]

@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file.

    Args:
        filepath: Path to the file
        content: Content to write
    """
    Path(filepath).write_text(content)
    return f"Written to {filepath}"
```

### Database

```python
import sqlite3
from strands import tool

@tool
def query_db(sql: str) -> str:
    """Execute read-only SQL query.

    Args:
        sql: SELECT query to execute
    """
    if not sql.strip().upper().startswith("SELECT"):
        return "Only SELECT queries allowed"

    conn = sqlite3.connect("data.db")
    cursor = conn.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return str(results)
```

---

## Built-in Tools (strands_tools)

```python
from strands_tools import (
    calculator,      # Math operations
    file_read,       # Read files
    shell,           # Execute shell commands
    current_time,    # Get current time
    swarm,           # Multi-agent orchestration
)

agent = Agent(tools=[calculator, file_read, shell])
```

---

## Tool Best Practices

1. **Clear Descriptions**: Model uses docstring to decide when to call
2. **Specific Names**: `get_user_profile` > `get_data`
3. **Type Safety**: Always use type hints
4. **Error Messages**: Return helpful errors, don't raise
5. **Limit Output**: Truncate large responses
6. **Timeout External Calls**: Prevent hanging

```python
@tool
def best_practice_tool(user_id: str) -> str:
    """Get user profile by ID. Use when user asks about account details.

    Args:
        user_id: The unique user identifier
    """
    try:
        user = db.get_user(user_id, timeout=5)
        if not user:
            return f"User {user_id} not found"
        return f"Name: {user.name}, Email: {user.email}"
    except TimeoutError:
        return "Database timeout, please try again"
    except Exception as e:
        return f"Error fetching user: {str(e)}"
```
