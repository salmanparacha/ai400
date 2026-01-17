# FastAPI Microservice Patterns

Best practices for building microservices with FastAPI.

## Table of Contents

- Service Communication
- HTTP Client Management
- Circuit Breakers
- Retry Logic
- Service Discovery
- Configuration Management
- Health Checks

## Service Communication

### HTTP Client with httpx

Always use async HTTP clients for non-blocking I/O:

```python
import httpx
from contextlib import asynccontextmanager

http_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    # Startup: Create HTTP client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0),
        limits=httpx.Limits(max_connections=100)
    )
    yield
    # Shutdown: Close client
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

def get_http_client() -> httpx.AsyncClient:
    return http_client
```

### Making Service Calls

```python
async def call_user_service(
    user_id: int,
    client: httpx.AsyncClient = Depends(get_http_client)
) -> dict:
    try:
        response = await client.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            timeout=5.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(404, "User not found")
        raise HTTPException(503, "User service unavailable")
    except httpx.RequestError:
        raise HTTPException(503, "User service unreachable")
```

## Retry Logic

### Simple Retry with tenacity

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_product(product_id: int, client: httpx.AsyncClient):
    response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    response.raise_for_status()
    return response.json()
```

### Conditional Retry

```python
from tenacity import retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.RequestError),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_with_retry(url: str, client: httpx.AsyncClient):
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

## Circuit Breaker Pattern

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func):
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half-open"
            else:
                raise HTTPException(503, "Circuit breaker is open")

        try:
            result = func()
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.failures >= self.failure_threshold:
                self.state = "open"

            raise e

# Usage
inventory_circuit = CircuitBreaker()

async def get_inventory(product_id: int):
    return inventory_circuit.call(
        lambda: fetch_inventory(product_id)
    )
```

## Service Configuration

### Environment-Based Settings

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Service info
    service_name: str = "order-service"
    service_version: str = "1.0.0"

    # External services
    user_service_url: str
    product_service_url: str
    inventory_service_url: str

    # Timeouts
    service_timeout: float = 5.0
    database_timeout: float = 10.0

    # Circuit breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

## Health Checks

### Comprehensive Health Check

```python
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    health_status = {
        "service": "order-service",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception:
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"

    # External service checks
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/health",
                timeout=2.0
            )
            health_status["checks"]["user_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        health_status["checks"]["user_service"] = "unhealthy"

    return health_status
```

### Liveness vs Readiness

```python
@app.get("/health/live")
async def liveness():
    """Check if service is running."""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """Check if service is ready to handle requests."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(503, "Service not ready")
```

## API Versioning

```python
from fastapi import APIRouter

# Version 1
router_v1 = APIRouter(prefix="/api/v1")

@router_v1.get("/orders")
async def get_orders_v1():
    return {"version": "v1", "orders": []}

# Version 2
router_v2 = APIRouter(prefix="/api/v2")

@router_v2.get("/orders")
async def get_orders_v2():
    return {"version": "v2", "orders": [], "pagination": {}}

app.include_router(router_v1)
app.include_router(router_v2)
```

## Request Tracing

```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

## Service-to-Service Authentication

```python
from fastapi import Header, HTTPException

async def verify_service_token(x_service_token: str = Header(...)):
    """Verify service-to-service authentication token."""
    if x_service_token != settings.service_secret:
        raise HTTPException(403, "Invalid service token")
    return x_service_token

@router.post("/internal/orders")
async def create_internal_order(
    order: OrderCreate,
    token: str = Depends(verify_service_token)
):
    # Internal endpoint for service-to-service calls
    pass
```
