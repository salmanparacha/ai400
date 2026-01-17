# Model Configuration

This reference covers configuring different model providers for Strands agents, including AWS Bedrock, simple model strings, and production configurations.

## Table of Contents

- [Simple Model Configuration](#simple-model-configuration)
- [AWS Bedrock Configuration](#aws-bedrock-configuration)
- [Dictionary Configuration](#dictionary-configuration)
- [Production Settings](#production-settings)
- [Model Selection Guide](#model-selection-guide)

## Simple Model Configuration

The simplest way to configure a model is using a model ID string:

```python
from strands import Agent

# Using simple model ID
agent = Agent(model="claude-3-5-sonnet-20241022")
```

**Common Model IDs:**
- `claude-3-5-sonnet-20241022` - Latest Claude 3.5 Sonnet
- `claude-3-opus-20240229` - Claude 3 Opus
- `claude-3-haiku-20240307` - Claude 3 Haiku

## AWS Bedrock Configuration

For production environments, use AWS Bedrock with detailed configuration:

### Basic Bedrock Setup

```python
from strands import Agent
from strands.models import BedrockModel

# Create Bedrock model configuration
bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1"
)

# Create agent with Bedrock model
agent = Agent(model=bedrock_model)
```

### Full Bedrock Configuration

```python
from strands.models import BedrockModel

bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-west-2",
    temperature=0.7,
    max_tokens=4096,
    top_p=0.9
)

agent = Agent(
    model=bedrock_model,
    system_prompt="You are a helpful assistant.",
    tools=[calculator, current_time]
)
```

**Bedrock Model Parameters:**
- `model_id`: Full Bedrock model identifier (required)
- `region`: AWS region where model is available (required)
- `temperature`: Randomness in responses (0.0-1.0, default: 1.0)
- `max_tokens`: Maximum tokens in response (default: 4096)
- `top_p`: Nucleus sampling parameter (0.0-1.0, default: 1.0)

### Bedrock Model IDs

```python
# Claude 3.5 Sonnet (Latest)
"anthropic.claude-3-5-sonnet-20241022-v2:0"

# Claude 3 Opus
"anthropic.claude-3-opus-20240229-v1:0"

# Claude 3 Haiku
"anthropic.claude-3-haiku-20240307-v1:0"

# Claude 3.5 Sonnet (Previous version)
"anthropic.claude-3-5-sonnet-20240620-v1:0"
```

### AWS Credentials

Bedrock requires AWS credentials. Configure them via:

**Environment variables:**
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

**AWS credentials file** (`~/.aws/credentials`):
```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
```

**IAM role** (for EC2/ECS/Lambda):
- Attach IAM role with Bedrock permissions to your compute resource

### Checking Current Model

```python
# Get the currently configured model
current_model = agent.model
print(f"Using model: {current_model}")
```

## Dictionary Configuration

Create agents from dictionary configuration (useful for loading from JSON/YAML):

### Python Dictionary

```python
from strands import Agent

config = {
    "model": "claude-3-5-sonnet-20241022",
    "system_prompt": "You are a helpful coding assistant.",
    "tools": ["strands_tools.calculator", "my_app.tools.file_reader"]
}

agent = Agent(**config)
```

### JSON Configuration File

**config.json:**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "system_prompt": "You are a coding assistant specializing in Python.",
  "tools": [
    "strands_tools.file_read",
    "strands_tools.shell",
    "my_app.tools.custom_tool"
  ]
}
```

**Loading from JSON:**
```python
import json
from strands import Agent

with open("config.json") as f:
    config = json.load(f)

agent = Agent(**config)
```

### Environment-Specific Configurations

```python
import os
import json

def load_agent_config(environment="development"):
    """Load configuration based on environment."""
    config_file = f"configs/{environment}.json"

    with open(config_file) as f:
        return json.load(f)

# Load appropriate config
env = os.getenv("ENVIRONMENT", "development")
config = load_agent_config(env)

# Create agent
agent = Agent(**config)
```

**configs/development.json:**
```json
{
  "model": "claude-3-haiku-20240307",
  "system_prompt": "Development assistant",
  "tools": ["strands_tools.calculator"]
}
```

**configs/production.json:**
```json
{
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "system_prompt": "Production assistant",
  "tools": [
    "strands_tools.calculator",
    "strands_tools.current_time",
    "app.tools.database_query"
  ]
}
```

## Production Settings

### Temperature Control

Lower temperature for consistent, focused responses:

```python
# Production: Lower temperature for consistency
production_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1",
    temperature=0.3,  # More deterministic
    max_tokens=4096
)

# Creative tasks: Higher temperature
creative_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1",
    temperature=0.9,  # More creative
    max_tokens=4096
)
```

### Token Limits

Set appropriate max_tokens based on use case:

```python
# Short responses (summaries, classifications)
compact_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1",
    max_tokens=500
)

# Long responses (reports, analysis)
verbose_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1",
    max_tokens=8000
)
```

### Region Selection

Choose region based on:
- **Latency**: Closer to your users
- **Availability**: Model availability varies by region
- **Cost**: Pricing may differ by region

```python
# US East (Virginia) - Often first for new models
us_east_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1"
)

# US West (Oregon)
us_west_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-west-2"
)

# Europe (Frankfurt)
eu_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="eu-central-1"
)
```

### Error Handling

```python
from strands.models import BedrockModel

def create_agent_with_fallback():
    """Create agent with fallback model if Bedrock fails."""
    try:
        # Try Bedrock first
        model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            region="us-east-1"
        )
        agent = Agent(model=model)
        return agent
    except Exception as e:
        print(f"Bedrock unavailable: {e}")
        print("Falling back to simple model")
        # Fallback to simple model
        return Agent(model="claude-3-5-sonnet-20241022")
```

## Model Selection Guide

### By Use Case

**Fast responses, lower cost:**
```python
# Use Haiku
agent = Agent(model="claude-3-haiku-20240307")
```

**Balanced performance:**
```python
# Use Sonnet (recommended for most cases)
agent = Agent(model="claude-3-5-sonnet-20241022")
```

**Complex reasoning, highest quality:**
```python
# Use Opus
agent = Agent(model="claude-3-opus-20240229")
```

### By Environment

**Development:**
```python
# Simpler model for faster iteration
dev_agent = Agent(
    model="claude-3-haiku-20240307",
    temperature=0.7
)
```

**Staging:**
```python
# Production-like model
staging_agent = Agent(
    model="claude-3-5-sonnet-20241022",
    temperature=0.5
)
```

**Production:**
```python
# Full Bedrock configuration
prod_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region="us-east-1",
    temperature=0.3,
    max_tokens=4096,
    top_p=0.9
)

prod_agent = Agent(
    model=prod_model,
    system_prompt="Production assistant with strict guidelines"
)
```

### By Task Type

**Classification/Extraction:**
```python
# Low temperature, short responses
classifier = Agent(
    model=BedrockModel(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region="us-east-1",
        temperature=0.1,
        max_tokens=100
    )
)
```

**Creative Writing:**
```python
# High temperature, long responses
writer = Agent(
    model=BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1",
        temperature=0.9,
        max_tokens=8000
    )
)
```

**Code Generation:**
```python
# Medium-low temperature, technical model
coder = Agent(
    model=BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1",
        temperature=0.3,
        max_tokens=4096
    ),
    system_prompt="You are an expert programmer."
)
```
