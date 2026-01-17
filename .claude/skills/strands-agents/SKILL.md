---
name: strands-agents
description: "Build AI agents using AWS Strands SDK from simple single agents to production-grade multi-agent systems. Use when: (1) Creating AI agents with custom tools, (2) Building multi-agent workflows, (3) Configuring agents with AWS Bedrock, (4) Implementing production agents with monitoring and logging, (5) Integrating AI agents into applications. Includes templates for minimal agents, custom tools, sequential workflows, and production deployments with comprehensive error handling."
---

# Strands Agents Development

Build AI agents with AWS Strands SDK, from simple hello world agents to production-ready systems with custom tools, multi-agent workflows, and AWS Bedrock integration.

## Quick Start

### Creating a New Project

Use the project generator script to scaffold a new Strands agent project:

```bash
python scripts/create_project.py <template> <project-name>
```

Available templates:
- `minimal` - Simple agent with built-in tools (good for learning)
- `custom-tools` - Agent with custom tool examples
- `multi-agent` - Sequential workflow with specialized agents
- `production` - Production-ready with Bedrock, logging, error handling

Example:
```bash
python scripts/create_project.py minimal my-first-agent
cd my-first-agent
pip install -r requirements.txt
python main.py
```

## Project Templates

### 1. Minimal Agent

**When to use:** Learning Strands, quick prototypes, simple single-purpose agents

**What's included:**
- Basic agent with built-in tools (calculator, current_time)
- Simple query examples
- Interactive mode

**Location:** `assets/minimal/`

**Key features:**
```python
from strands import Agent
from strands_tools import calculator, current_time

# Create agent
agent = Agent(tools=[calculator, current_time])

# Use agent
response = agent("What time is it? Also calculate 10 + 20")
print(response.message)
```

### 2. Custom Tools Agent

**When to use:** Building agents with domain-specific capabilities, adding custom functionality

**What's included:**
- Examples of custom tools using `@tool` decorator
- Letter counter, word reverser, text analyzer examples
- Mixed built-in and custom tools

**Location:** `assets/custom-tools/`

**Key features:**
```python
from strands import Agent, tool

@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word: The input word to search in
        letter: The specific letter to count

    Returns:
        The number of occurrences
    """
    return word.lower().count(letter.lower())

agent = Agent(tools=[calculator, letter_counter])
```

**For detailed patterns:** See [references/custom-tools-patterns.md](references/custom-tools-patterns.md)

### 3. Multi-Agent Workflow

**When to use:** Complex tasks requiring specialized processing stages, research-analyze-report pipelines

**What's included:**
- Sequential workflow pattern (researcher → analyst → writer)
- Specialized agent roles with custom system prompts
- Data passing between agents
- Progress tracking

**Location:** `assets/multi-agent/`

**Key features:**
```python
from strands import Agent

# Specialized agents
researcher = Agent(
    system_prompt="You are a research specialist...",
    callback_handler=None  # Silent
)

analyst = Agent(system_prompt="You are a data analyst...")
writer = Agent(system_prompt="You are a professional writer...")

# Sequential workflow
research = researcher(f"Research {topic}")
analysis = analyst(f"Analyze: {research}")
report = writer(f"Write report: {analysis}")
```

**For detailed patterns:** See [references/multi-agent-patterns.md](references/multi-agent-patterns.md)

### 4. Production Agent

**When to use:** Production deployments, AWS Bedrock integration, enterprise applications

**What's included:**
- AWS Bedrock model configuration
- Comprehensive error handling with fallbacks
- Structured logging to file and console
- Metrics collection (execution time, tool usage)
- Environment-based configuration
- Graceful degradation

**Location:** `assets/production/`

**Setup required:**
1. Install requirements (includes boto3)
2. Copy `.env.example` to `.env`
3. Configure AWS credentials and region

**Key features:**
```python
from strands.models import BedrockModel

# Production model config
model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1",
    temperature=0.3,
    max_tokens=4096
)

agent = Agent(
    model=model,
    tools=[calculator],
    callback_handler=metrics_collector
)
```

**For detailed patterns:**
- Model configuration: [references/model-configuration.md](references/model-configuration.md)
- Logging: [references/callback-handlers.md](references/callback-handlers.md)

## Core Concepts

### Creating Agents

Basic agent creation:

```python
from strands import Agent

# Simplest form
agent = Agent()

# With tools
agent = Agent(tools=[calculator, current_time])

# With custom system prompt
agent = Agent(
    system_prompt="You are a helpful coding assistant.",
    tools=[calculator]
)

# With specific model
agent = Agent(model="claude-3-5-sonnet-20241022")
```

### Using Agents

```python
# Simple query
response = agent("What is 42 * 17?")
print(response.message)

# Agent automatically selects and uses tools
response = agent("""
1. What time is it?
2. Calculate 100 / 5
3. Count R's in 'strawberry'
""")
```

### Custom Tools

Create tools with the `@tool` decorator:

```python
from strands import tool

@tool
def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculate final price after discount.

    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)

    Returns:
        Final price after discount
    """
    return price * (1 - discount_percent / 100)

agent = Agent(tools=[calculate_discount])
```

**Requirements for custom tools:**
- Use `@tool` decorator
- Include comprehensive docstring (agent uses this to understand the tool)
- Add type hints for all parameters and return value
- Handle errors gracefully

**See [references/custom-tools-patterns.md](references/custom-tools-patterns.md) for:**
- Input validation
- Error handling
- Optional parameters
- Best practices

### Multi-Agent Workflows

Create specialized agents and chain them:

```python
# Create specialized agents
planner = Agent(system_prompt="You create detailed plans.")
executor = Agent(system_prompt="You execute plans step by step.")
reviewer = Agent(system_prompt="You review and verify work.")

# Sequential workflow
plan = planner("Create a plan for building a web app")
execution = executor(f"Execute this plan: {plan}")
review = reviewer(f"Review this work: {execution}")
```

**Common patterns:**
- Sequential processing (research → analyze → write)
- Specialized roles (data collector, analyst, writer)
- Context accumulation (each agent adds to shared context)
- Validation between steps

**See [references/multi-agent-patterns.md](references/multi-agent-patterns.md) for:**
- Workflow patterns
- Error handling in workflows
- Parallel processing
- Fallback strategies

### Model Configuration

#### Simple Configuration

```python
agent = Agent(model="claude-3-5-sonnet-20241022")
```

#### AWS Bedrock Configuration

```python
from strands.models import BedrockModel

model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1",
    temperature=0.3,  # Lower = more focused
    max_tokens=4096,
    top_p=0.9
)

agent = Agent(model=model)
```

**AWS credentials setup:**
```bash
# Environment variables
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

**See [references/model-configuration.md](references/model-configuration.md) for:**
- Bedrock model IDs
- Environment-specific configurations
- Temperature and token settings
- Region selection
- Error handling and fallbacks

### Callback Handlers

Monitor and log agent execution:

```python
def custom_callback(**kwargs):
    if "data" in kwargs:
        print(kwargs["data"], end="")
    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        print(f"\n[Using: {tool.get('name')}]\n")

agent = Agent(
    tools=[calculator],
    callback_handler=custom_callback
)
```

**Use cases:**
- Monitor agent responses (streaming text)
- Track tool usage
- Log to files
- Collect metrics
- Update custom UI
- Debug agent behavior

**See [references/callback-handlers.md](references/callback-handlers.md) for:**
- Built-in handlers
- Custom logging
- Metrics collection
- Production patterns

## Common Workflows

### Building a Simple Agent

1. Create project:
   ```bash
   python scripts/create_project.py minimal my-agent
   cd my-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run:
   ```bash
   python main.py
   ```

4. Add custom tools in `main.py`:
   ```python
   @tool
   def my_tool(input: str) -> str:
       """My custom tool."""
       return f"Processed: {input}"

   agent = Agent(tools=[calculator, my_tool])
   ```

### Building a Multi-Agent System

1. Create project:
   ```bash
   python scripts/create_project.py multi-agent my-workflow
   cd my-workflow
   pip install -r requirements.txt
   ```

2. Customize agents in `main.py`:
   - Update system prompts for your domain
   - Add custom tools to each agent
   - Modify workflow logic

3. Run:
   ```bash
   python main.py
   ```

### Deploying to Production

1. Create production project:
   ```bash
   python scripts/create_project.py production my-prod-agent
   cd my-prod-agent
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. Test locally:
   ```bash
   python main.py
   ```

4. Deploy (example with Docker):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]
   ```

## Best Practices

### Agent Design

**Use focused system prompts:**
```python
# Good: Specific and actionable
Agent(system_prompt="""You are a Python code reviewer.
Focus on: security, performance, PEP 8 compliance.
Provide specific line numbers and fixes.""")

# Avoid: Too vague
Agent(system_prompt="You help with code")
```

**Choose appropriate models:**
- Fast responses: `claude-3-haiku-20240307`
- Balanced: `claude-3-5-sonnet-20241022` (recommended)
- Complex reasoning: `claude-3-opus-20240229`

### Custom Tools

**Write clear docstrings:**
```python
@tool
def search_database(query: str, limit: int = 10) -> list:
    """
    Search the product database.

    Use this when user asks about products or inventory.

    Args:
        query: Search query string
        limit: Maximum results (default: 10)

    Returns:
        List of matching products
    """
    # Implementation
```

**Handle errors gracefully:**
```python
@tool
def read_file(filepath: str) -> str:
    """Read file contents."""
    try:
        with open(filepath) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

### Multi-Agent Systems

**Keep agents specialized:**
```python
# Good: Clear specialization
data_agent = Agent(system_prompt="Collect data")
analysis_agent = Agent(system_prompt="Analyze data")

# Avoid: Overlapping responsibilities
agent = Agent(system_prompt="Collect and analyze data")
```

**Pass minimal context:**
```python
# Good: Pass only what's needed
summary = agent1(task)
result = agent2(f"Analyze: {summary}")

# Avoid: Passing everything
full_history = agent1.get_full_history()
result = agent2(full_history)  # Too much context
```

### Production Deployment

**Use environment variables:**
```python
import os

region = os.getenv("AWS_REGION", "us-east-1")
temperature = float(os.getenv("MODEL_TEMPERATURE", "0.3"))
```

**Implement error handling:**
```python
try:
    response = agent(query)
except Exception as e:
    logger.error(f"Agent error: {e}")
    # Fallback or notify
```

**Log important events:**
```python
logger.info(f"Processing query: {query}")
logger.info(f"Tools used: {tool_count}")
logger.error(f"Error: {error}")
```

## Installation

Install Strands agents SDK:

```bash
pip install strands-agents
```

For AWS Bedrock support:

```bash
pip install strands-agents boto3
```

## Resources

- **scripts/create_project.py** - Project scaffolding tool
- **assets/** - Project templates (minimal, custom-tools, multi-agent, production)
- **references/custom-tools-patterns.md** - Custom tool creation and best practices
- **references/multi-agent-patterns.md** - Multi-agent workflows and collaboration
- **references/model-configuration.md** - Model configuration and AWS Bedrock setup
- **references/callback-handlers.md** - Monitoring, logging, and debugging patterns
