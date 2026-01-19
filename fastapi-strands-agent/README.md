# FastAPI Agent with AWS Strands & Tavily Search

An intelligent AI agent using the **AWS Strands SDK**, wrapped in a **FastAPI** application. Features session-based agent pooling, persistent conversation history, real-time web search, and model flexibility.

## Features

- **Session-Based Agent Pooling**: Agents are cached per session with 10-minute TTL, avoiding repeated disk I/O
- **AI Models**: Amazon Nova Lite (default) or Anthropic Claude 3 Sonnet via AWS Bedrock
- **Web Search**: Integrated **Tavily Search** tool for real-time information retrieval
- **Persistent Memory**: Sliding window conversation history (10 turns), persisted to local disk
- **REST API**: Clean API with Swagger UI documentation
- **Privacy**: Automatically strips internal "thinking" traces from responses

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌─────────────────────────────────────┐  │
│  │   /chat      │────▶│            AgentPool                 │  │
│  │   /health    │     │  ┌─────────────────────────────────┐ │  │
│  │   /history   │     │  │ session_1:nova-lite → Agent     │ │  │
│  │   /session   │     │  │ session_2:anthropic → Agent     │ │  │
│  └──────────────┘     │  │ session_3:nova-lite → Agent     │ │  │
│                       │  └─────────────────────────────────┘ │  │
│                       │                                       │  │
│                       │  • TTL: 10 minutes                   │  │
│                       │  • Max agents: 100                   │  │
│                       │  • Background cleanup                │  │
│                       └─────────────────────────────────────┘  │
│                                      │                          │
│                                      ▼                          │
│                       ┌─────────────────────────────────────┐  │
│                       │         FileSessionManager          │  │
│                       │         (.sessions/ directory)      │  │
│                       └─────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
First request for session:
├── AgentPool.get(session_id) → Cache miss
├── Create Agent (loads history from disk ONCE)
├── Agent.invoke_async(message)
├── FileSessionManager saves to disk
└── Return response

Subsequent requests (within 10 min):
├── AgentPool.get(session_id) → Cache hit (no disk read!)
├── Agent.invoke_async(message)
├── FileSessionManager saves to disk
└── Return response

After 10 min idle:
├── Background task evicts agent from pool
└── Next request triggers fresh load from disk
```

### Performance Comparison

| Scenario | Before (per-request agent) | After (AgentPool) |
|----------|---------------------------|-------------------|
| 20 messages in 10 min | 20 disk reads + 20 writes | 1 disk read + 20 writes |
| Memory usage | Minimal (GC'd each request) | Bounded (max 100 agents) |
| Latency | Higher (init overhead) | Lower (reuse agent) |

## Prerequisites

- Python 3.10+
- AWS Credentials configured (e.g., `~/.aws/credentials` or env vars)
- [Tavily API Key](https://tavily.com/) (Free tier available)
- [uv](https://github.com/astral-sh/uv) (Recommended package manager)

## Installation

1. **Clone/Enter Directory**:
    ```bash
    cd fastapi-strands-agent
    ```

2. **Install Dependencies**:
    ```bash
    uv sync
    # Or with pip: pip install -r requirements.txt
    ```

3. **Configure Environment**:
    Create a `.env` file in the root directory:
    ```bash
    TAVILY_API_KEY=tvly-xxxxxxxxxxxx
    ```

## Usage

### Start the Server
```bash
uv run fastapi dev app/main.py
```
Server runs at `http://127.0.0.1:8000`.

### Interactive Documentation (Swagger UI)
Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

## API Endpoints

### 1. Chat (`POST /chat`)
Send a message to the agent.

**Request:**
```json
{
  "message": "What is the latest news on SpaceX?",
  "session_id": "user-session-1",
  "model_provider": "nova-lite"
}
```

**Parameters:**
- `message`: Your message to the agent
- `session_id`: Unique ID to track conversation history
- `model_provider`: Optional. `"nova-lite"` (default) or `"anthropic"`

**Response:**
```json
{
  "response": "Here's the latest SpaceX news...",
  "session_id": "user-session-1"
}
```

### 2. Health Check (`GET /health`)
Check server status and active sessions.

```bash
curl http://127.0.0.1:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 3,
  "sessions": ["user-1", "user-2", "user-3"]
}
```

### 3. History (`GET /history/{session_id}`)
View the stored conversation context for a session.

```bash
curl http://127.0.0.1:8000/history/user-session-1
```

### 4. Delete Session (`DELETE /session/{session_id}`)
Remove an agent from the pool (forces fresh load on next request).

```bash
curl -X DELETE "http://127.0.0.1:8000/session/user-session-1?provider=nova-lite"
```

## Project Structure

```
fastapi-strands-agent/
├── app/
│   ├── main.py           # FastAPI app, endpoints, lifespan
│   ├── agent_pool.py     # Session-based agent pooling with TTL
│   └── models.py         # Pydantic request/response models
├── tests/
│   └── test_api.py       # Pytest suite with mocked agents
├── .sessions/            # Local storage for conversation history
├── .env                  # Secrets (API Keys)
└── pyproject.toml        # Dependencies
```

## Configuration

The `AgentPool` can be configured in `app/main.py`:

```python
agent_pool = AgentPool(
    ttl_minutes=10,      # How long idle agents stay in memory
    max_agents=100,      # Maximum concurrent agents
    session_dir=".sessions",  # Conversation persistence directory
    window_size=10,      # Sliding window for conversation context
)
```

## Testing

Run the test suite:
```bash
PYTHONPATH=. uv run pytest
```

Run with verbose output:
```bash
PYTHONPATH=. uv run pytest -v
```

## Key Components

### AgentPool (`app/agent_pool.py`)

Manages agent lifecycle with:
- **TTL-based eviction**: Agents removed after 10 min idle
- **LRU eviction**: Oldest agent removed when at capacity
- **Thread-safe**: Uses `asyncio.Lock` for concurrent access
- **Background cleanup**: Periodic task removes expired agents

### FileSessionManager (Strands SDK)

Handles conversation persistence:
- Saves full history to `.sessions/` directory
- Loaded once when agent is created
- Subsequent messages append without re-reading

### SlidingWindowConversationManager (Strands SDK)

Controls what's sent to the LLM:
- Keeps last 10 conversation turns
- Full history still saved to disk
- Reduces token usage and cost

## Supported Models

| Provider | Model ID | Description |
|----------|----------|-------------|
| `nova-lite` | `amazon.nova-lite-v1:0` | Fast, cost-effective (default) |
| `anthropic` | `anthropic.claude-3-sonnet-20240229-v1:0` | More capable, higher cost |
| Custom | Any Bedrock model ID | Pass directly as `model_provider` |

## AWS Lambda Deployment

### Overview

While this application is optimized for long-running containers (ECS/Fargate) with agent pooling, it can be deployed on AWS Lambda with trade-offs.

### Lambda Architecture Changes

**Key Challenge**: Lambda's stateless nature eliminates the agent pooling benefits, causing performance degradation due to agent recreation and disk I/O on every request.

**Solution**: Use Lambda's execution context reuse with global variables to partially restore caching benefits.

### Lambda Implementation

```python
# lambda_handler.py
from mangum import Mangum
from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from datetime import datetime, timedelta
import os

# Global initialization - runs once per container
bedrock_model = BedrockModel(model_id="amazon.nova-lite-v1:0")
agent_cache = {}
CACHE_TTL = timedelta(minutes=10)

# FastAPI app with Mangum adapter
from app.main import app
handler = Mangum(app)

def create_agent(session_id: str, provider: str = "nova-lite"):
    """Create agent with global model reuse"""
    model_ids = {
        "nova-lite": "amazon.nova-lite-v1:0",
        "anthropic": "anthropic.claude-3-sonnet-20240229-v1:0"
    }
    
    model = BedrockModel(model_id=model_ids.get(provider, provider))
    session_manager = FileSessionManager(
        session_id=session_id,
        storage_dir="/tmp/.sessions"  # Lambda writable directory
    )
    
    return Agent(
        model=model,
        session_manager=session_manager,
        tools=[tavily] if os.getenv("TAVILY_API_KEY") else []
    )

def get_cached_agent(session_id: str, provider: str = "nova-lite"):
    """Get agent from cache or create new one"""
    cache_key = f"{session_id}:{provider}"
    now = datetime.now()
    
    # Clean expired agents
    expired = [k for k, (_, timestamp) in agent_cache.items() 
               if now - timestamp > CACHE_TTL]
    for k in expired:
        del agent_cache[k]
    
    # Return cached or create new
    if cache_key in agent_cache:
        agent, _ = agent_cache[cache_key]
        agent_cache[cache_key] = (agent, now)  # Update access time
        return agent
    else:
        agent = create_agent(session_id, provider)
        agent_cache[cache_key] = (agent, now)
        return agent

def lambda_handler(event, context):
    return handler(event, context)
```

### Deployment Configuration

```yaml
# template.yaml (AWS SAM)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  StrandsAgentFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: lambda_handler.lambda_handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 1024
      Environment:
        Variables:
          TAVILY_API_KEY: !Ref TavilyApiKey
      Events:
        HttpApi:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY

Parameters:
  TavilyApiKey:
    Type: String
    NoEcho: true
```

### Lambda vs Container Comparison

| Aspect | Container (ECS/Fargate) | Lambda with Global Cache |
|--------|------------------------|-------------------------|
| Agent Pooling | ✅ Full pooling across requests | ⚠️ Per-container only |
| Cold Start | ✅ Minimal after warmup | ❌ 2-5 seconds |
| Memory Efficiency | ✅ Shared across sessions | ⚠️ Cache grows until container dies |
| Cost (Low Traffic) | ❌ Always running | ✅ Pay per request |
| Cost (High Traffic) | ✅ Fixed cost | ❌ Can be expensive |
| Persistence Guarantee | ✅ Reliable | ❌ No guarantees |

### Lambda Limitations

- **Container Reuse**: AWS controls when containers are reused (5-15 min typical)
- **Memory Growth**: Agent cache grows until container dies
- **Cold Starts**: Still occur, eliminating pooling benefits
- **Session Storage**: Limited to `/tmp` (512MB max)

### Recommendation

**Use Lambda when**:
- Low, sporadic traffic
- Cost optimization priority
- Serverless architecture requirement

**Use ECS/Fargate when**:
- Consistent traffic patterns
- Performance optimization priority
- Need reliable agent pooling benefits

## License

MIT
