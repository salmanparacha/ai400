# Custom Tools Patterns

This reference covers creating custom tools for Strands agents with proper validation, error handling, and best practices.

## Table of Contents

- [Basic Tool Creation](#basic-tool-creation)
- [Tool Parameters and Validation](#tool-parameters-and-validation)
- [Error Handling](#error-handling)
- [Loading Tools](#loading-tools)
- [Best Practices](#best-practices)

## Basic Tool Creation

Create custom tools using the `@tool` decorator:

```python
from strands import tool

@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word: The input word to search in
        letter: The specific letter to count

    Returns:
        The number of occurrences of the letter in the word
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0
    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")
    return word.lower().count(letter.lower())
```

**Key requirements:**
- Use `@tool` decorator from `strands`
- Include comprehensive docstring (used by the agent to understand the tool)
- Type hints for all parameters and return value
- Clear parameter descriptions in docstring

## Tool Parameters and Validation

### Type Hints

Always use type hints - they help the agent understand expected input types:

```python
@tool
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate final price after discount."""
    return price * (1 - discount_percent / 100)
```

### Input Validation

Validate inputs early and provide clear error messages:

```python
@tool
def divide_numbers(dividend: float, divisor: float) -> float:
    """
    Divide two numbers.

    Args:
        dividend: The number to be divided
        divisor: The number to divide by

    Returns:
        The result of division
    """
    if divisor == 0:
        raise ValueError("Cannot divide by zero")
    if not isinstance(dividend, (int, float)) or not isinstance(divisor, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return dividend / divisor
```

### Optional Parameters

Use default values for optional parameters:

```python
@tool
def search_text(text: str, query: str, case_sensitive: bool = False) -> int:
    """
    Search for a query string within text.

    Args:
        text: The text to search in
        query: The string to search for
        case_sensitive: Whether search should be case-sensitive (default: False)

    Returns:
        Number of occurrences found
    """
    if not case_sensitive:
        text = text.lower()
        query = query.lower()
    return text.count(query)
```

## Error Handling

### Graceful Failures

Return meaningful error information instead of crashing:

```python
@tool
def read_file_content(filepath: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        filepath: Path to the file to read

    Returns:
        File contents as a string, or error message if file cannot be read
    """
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found"
    except PermissionError:
        return f"Error: Permission denied reading '{filepath}'"
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

### Input Sanitization

Sanitize inputs for security-sensitive operations:

```python
import os
from pathlib import Path

@tool
def safe_read_file(filename: str, base_dir: str = "/safe/directory") -> str:
    """
    Safely read a file from a restricted directory.

    Args:
        filename: Name of the file (not full path)
        base_dir: Base directory to read from (default: /safe/directory)

    Returns:
        File contents or error message
    """
    # Prevent directory traversal
    safe_path = Path(base_dir) / Path(filename).name

    if not safe_path.exists():
        return f"Error: File does not exist"

    try:
        return safe_path.read_text()
    except Exception as e:
        return f"Error: {str(e)}"
```

## Loading Tools

### From Built-in Tools

```python
from strands import Agent
from strands_tools import calculator, current_time, shell

agent = Agent(tools=[calculator, current_time, shell])
```

### From Custom Modules

```python
from strands import Agent
from my_app.tools import letter_counter, file_reader

agent = Agent(tools=[letter_counter, file_reader])
```

### Mix Built-in and Custom Tools

```python
from strands import Agent
from strands_tools import calculator
from my_tools import custom_analyzer

agent = Agent(tools=[calculator, custom_analyzer])
```

### From JSON Configuration

```json
{
  "tools": [
    "strands_tools.calculator",
    "strands_tools.current_time",
    "my_app.tools.letter_counter",
    "/path/to/custom_tool.py"
  ]
}
```

## Best Practices

### 1. Comprehensive Docstrings

The agent uses docstrings to understand when and how to use tools:

```python
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email to a recipient.

    Use this tool when the user wants to send an email or message someone.

    Args:
        to: Email address of the recipient
        subject: Subject line of the email
        body: Main content/message of the email

    Returns:
        Confirmation message with email status
    """
    # Implementation
    pass
```

### 2. Single Responsibility

Each tool should do one thing well:

```python
# Good: Focused tool
@tool
def count_words(text: str) -> int:
    """Count the number of words in text."""
    return len(text.split())

# Avoid: Tool doing too much
@tool
def analyze_text(text: str, operation: str) -> any:
    """Do various text operations."""  # Too vague
    if operation == "count_words":
        return len(text.split())
    elif operation == "count_chars":
        return len(text)
    # ... more operations
```

### 3. Return Consistent Types

Return the same type consistently:

```python
# Good
@tool
def get_user_age(user_id: str) -> int:
    """Get user's age."""
    user = find_user(user_id)
    if user:
        return user.age
    return -1  # Or raise exception

# Avoid: Inconsistent return types
@tool
def get_user_age(user_id: str):
    user = find_user(user_id)
    if user:
        return user.age
    return "User not found"  # Mixing int and str
```

### 4. Descriptive Names

Use clear, action-oriented names:

```python
# Good
@tool
def calculate_tax(income: float, rate: float) -> float:
    """Calculate tax amount based on income and rate."""
    return income * rate

# Avoid: Vague names
@tool
def process(x: float, y: float) -> float:
    """Process numbers."""
    return x * y
```

### 5. Handle Edge Cases

Consider edge cases in your implementation:

```python
@tool
def get_first_element(items: list) -> any:
    """
    Get the first element from a list.

    Args:
        items: List of items

    Returns:
        First element, or None if list is empty
    """
    if not items:
        return None
    return items[0]
```
