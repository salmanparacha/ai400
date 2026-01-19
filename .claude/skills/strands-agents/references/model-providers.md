# Model Providers Reference

## AWS Bedrock (Default)

```python
from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-20250514-v1:0",
    # Optional parameters
    max_tokens=4096,
    temperature=0.7,
    top_p=0.9,
    stop_sequences=["END"],
)

agent = Agent(model=model)
```

### Claude Models (Bedrock)

| Model | ID |
|-------|-----|
| Claude Sonnet 4 | `anthropic.claude-sonnet-4-20250514-v1:0` |
| Claude Sonnet 3.5 v2 | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| Claude Haiku 3.5 | `anthropic.claude-3-5-haiku-20241022-v1:0` |
| Claude Opus 3 | `anthropic.claude-3-opus-20240229-v1:0` |

### Amazon Nova Models (Bedrock)

| Model | ID | Use Case |
|-------|-----|----------|
| Nova Premier | `amazon.nova-premier-v1:0` | Complex tasks, highest capability |
| Nova Pro | `amazon.nova-pro-v1:0` | Balanced performance/cost |
| Nova Lite | `amazon.nova-lite-v1:0` | Fast, cost-effective |
| Nova Micro | `amazon.nova-micro-v1:0` | Lowest latency, text-only |
| Nova 2 Lite | `amazon.nova-2-lite-v1:0` | Step-by-step reasoning, 1M context |
| Nova 2 Pro | `amazon.nova-2-pro-v1:0` | Complex multistep tasks (Preview) |
| Nova Sonic | `amazon.nova-sonic-v1:0` | Multimodal audio/text |
| Nova Canvas | `amazon.nova-canvas-v1:0` | Image generation |
| Nova Reel | `amazon.nova-reel-v1:0` | Video generation |

#### Nova Example

```python
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="us.amazon.nova-premier-v1:0",
    temperature=0.3,
    top_p=0.8,
)

agent = Agent(model=model)
response = agent("Tell me about Amazon Bedrock.")
```

#### Nova 2 with Extended Thinking

Nova 2 models support thinking intensity levels (low, medium, high):

```python
model = BedrockModel(
    model_id="amazon.nova-2-lite-v1:0",
    # Nova 2 supports extended thinking with step-by-step reasoning
)
```

### Cross-Region Inference

```python
# Add region prefix for cross-region inference profiles
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0"  # 'us.' prefix
)

# Also works for Nova
model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0"
)
```

### With Guardrails

```python
model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-20250514-v1:0",
    guardrail_id="your-guardrail-id",
    guardrail_version="1",
    guardrail_trace="enabled",  # "enabled", "disabled", "enabled_full"
    guardrail_stream_processing_mode="sync",  # "sync", "async"
    guardrail_redact_input=True,
    guardrail_redact_input_message="Input blocked.",
    guardrail_redact_output=False,
    guardrail_redact_output_message="Output blocked.",
)
```

---

## Anthropic Direct

```python
from strands.models.anthropic import AnthropicModel

model = AnthropicModel(
    client_args={
        "api_key": "sk-ant-...",  # Or use ANTHROPIC_API_KEY env var
    },
    model_id="claude-sonnet-4-20250514",
    max_tokens=1024,
    params={
        "temperature": 0.7,
        "top_p": 0.9,
    }
)

agent = Agent(model=model)
```

### Anthropic Model IDs

| Model | ID |
|-------|-----|
| Claude Sonnet 4 | `claude-sonnet-4-20250514` |
| Claude Sonnet 3.5 | `claude-3-5-sonnet-20241022` |
| Claude Haiku 3.5 | `claude-3-5-haiku-20241022` |
| Claude Opus 3 | `claude-3-opus-20240229` |

---

## OpenAI

```python
from strands.models.openai import OpenAIModel

model = OpenAIModel(
    client_args={
        "api_key": "sk-...",  # Or use OPENAI_API_KEY env var
    },
    model_id="gpt-4o",
)

agent = Agent(model=model)
```

### OpenAI Model IDs

| Model | ID |
|-------|-----|
| GPT-4o | `gpt-4o` |
| GPT-4o mini | `gpt-4o-mini` |
| GPT-4 Turbo | `gpt-4-turbo` |
| o1 | `o1` |
| o1-mini | `o1-mini` |

---

## LlamaCpp (Local)

```python
from strands.models.llamacpp import LlamaCppModel

model = LlamaCppModel(
    base_url="http://localhost:8080",
    model_id="default",
)

agent = Agent(model=model)
```

---

## Amazon Nova API (Direct)

For direct Nova API access outside Bedrock:

```python
from strands import Agent
from strands_amazon_nova import NovaAPIModel
import os

model = NovaAPIModel(
    api_key=os.environ.get("NOVA_API_KEY"),
    model_id="nova-2-lite-v1",
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

agent = Agent(model=model)
response = await agent.invoke_async("Can you write a short story?")
```

---

## Shorthand Syntax

For quick prototyping, pass model ID directly:

```python
# Uses Bedrock by default
agent = Agent(model="anthropic.claude-3-5-sonnet-20241022-v2:0")

# Nova models
agent = Agent(model="amazon.nova-pro-v1:0")
```

---

## Model Selection Guide

| Need | Recommended Model |
|------|-------------------|
| Highest capability | Claude Opus 3, Nova Premier |
| Balanced performance | Claude Sonnet 4, Nova Pro |
| Fast & cheap | Claude Haiku 3.5, Nova Lite, Nova Micro |
| Extended reasoning | Nova 2 Lite, Nova 2 Pro |
| 1M+ context window | Nova 2 Lite |
| Audio/multimodal | Nova Sonic |
| Image generation | Nova Canvas |

---

## Environment Variables

| Provider | Variable |
|----------|----------|
| Bedrock | Uses AWS credentials (IAM, env vars, or credential file) |
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Nova API | `NOVA_API_KEY` |

---

## Common Parameters

All model providers support:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `max_tokens` | Maximum response tokens | Model-specific |
| `temperature` | Randomness (0-1) | 0.7 |
| `top_p` | Nucleus sampling | 0.9 |
| `stop_sequences` | Stop generation tokens | None |
