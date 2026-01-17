---
name: fastapi
description: Build FastAPI applications from hello world to production-ready APIs. Use when creating new FastAPI projects, building REST APIs, implementing CRUD operations with PostgreSQL, developing microservices, serving ML models via API, or working with async Python web applications. Includes project templates (minimal starter, CRUD with PostgreSQL, microservice architecture, ML API), comprehensive patterns for database operations, service integration, and model serving.
---

# FastAPI Development Skill

Build FastAPI applications with best practices, from simple hello world apps to production-ready APIs with databases, microservices, and ML model serving.

## Quick Start

### Creating a New Project

Use the project generator script to scaffold a new FastAPI project:

```bash
python scripts/create_project.py <template> <project-name>
```

Available templates:
- `minimal` - Simple starter with basic endpoints (hello world, health check)
- `crud` - Full CRUD API with PostgreSQL, SQLAlchemy, and async support
- `microservice` - Service-oriented architecture with external service integration
- `ml` - ML model serving with batch prediction support

Example:
```bash
python scripts/create_project.py crud my-api
cd my-api
pip install -r requirements.txt
fastapi dev main.py
```

## Project Templates

### 1. Minimal Starter

**When to use:** Learning FastAPI, prototyping, simple APIs without database

**What's included:**
- Basic FastAPI app with 4 endpoints
- Pydantic models for validation
- Auto-generated API docs

**Location:** `assets/minimal-starter/`

**Key features:**
```python
# Simple GET endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Path parameters
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# POST with Pydantic validation
@app.post("/echo")
async def echo_message(message: Message):
    return {"received": message.message}
```

### 2. CRUD API with PostgreSQL

**When to use:** Building APIs with database persistence, user management, standard REST APIs

**What's included:**
- PostgreSQL with SQLAlchemy (async)
- Full CRUD operations for Users and Items
- Pydantic schemas for validation
- Password hashing with bcrypt
- Environment-based configuration
- Relationship handling (one-to-many)

**Location:** `assets/crud-api/`

**Project structure:**
```
app/
├── config.py          # Settings with pydantic-settings
├── database.py        # Async SQLAlchemy setup
├── models.py          # Database models
├── schemas.py         # Pydantic request/response models
└── routers/
    ├── users.py       # User CRUD endpoints
    └── items.py       # Item CRUD endpoints
```

**Setup required:**
1. Install PostgreSQL
2. Copy `.env.example` to `.env`
3. Update `DATABASE_URL` in `.env`

**For detailed patterns:** See [references/crud-patterns.md](references/crud-patterns.md)

### 3. Microservice Template

**When to use:** Building service-oriented architectures, integrating external APIs, distributed systems

**What's included:**
- HTTP client management with httpx
- External service integration patterns
- Service-to-service communication
- Environment-based configuration for multiple services
- Health checks and readiness probes

**Location:** `assets/microservice/`

**Key patterns:**
- Async HTTP client lifecycle management
- Stock reservation pattern with external inventory service
- Graceful error handling for service failures
- CORS configuration

**For detailed patterns:** See [references/microservice-patterns.md](references/microservice-patterns.md)

### 4. ML API Template

**When to use:** Serving machine learning models, batch predictions, text/image classification APIs

**What's included:**
- Model loading on startup
- Single and batch prediction endpoints
- Mock sentiment analysis model (replace with your own)
- Proper model lifecycle management
- Input validation for ML features

**Location:** `assets/ml-api/`

**Supports:**
- Scikit-learn models (with joblib)
- PyTorch models
- TensorFlow/Keras models
- Hugging Face transformers

**Example usage:**
```python
# Load your model on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    models["my_model"] = joblib.load("models/model.pkl")
    yield
    models.clear()

# Prediction endpoint
@app.post("/predict")
async def predict(input_data: PredictionInput):
    model = get_model("my_model")
    prediction = model.predict([input_data.features])
    return {"prediction": float(prediction[0])}
```

**For detailed patterns:** See [references/ml-api-patterns.md](references/ml-api-patterns.md)

## Reference Documentation

### CRUD Patterns

**When to reference:** Building database-backed APIs, implementing CRUD operations, working with SQLAlchemy

**File:** `references/crud-patterns.md`

**Covers:**
- Async SQLAlchemy setup with PostgreSQL
- Creating, reading, updating, deleting records
- Relationships (one-to-many, many-to-many)
- Filtering, sorting, and pagination
- Transaction handling
- Error handling for database operations

### Microservice Patterns

**When to reference:** Building microservices, integrating external APIs, implementing resilience patterns

**File:** `references/microservice-patterns.md`

**Covers:**
- HTTP client management with httpx
- Retry logic with tenacity
- Circuit breaker pattern
- Health checks (liveness vs readiness)
- API versioning
- Request tracing
- Service-to-service authentication

### ML API Patterns

**When to reference:** Serving ML models, optimizing inference, handling different model types

**File:** `references/ml-api-patterns.md`

**Covers:**
- Model loading strategies (startup vs lazy loading)
- Single and batch predictions
- Input validation for ML features
- Image and text input handling
- Model versioning
- GPU support for PyTorch
- Performance optimization
- Monitoring and logging

## Common Workflows

### Building a Simple API

1. Create minimal project: `python scripts/create_project.py minimal my-app`
2. Navigate to project: `cd my-app`
3. Install dependencies: `pip install -r requirements.txt`
4. Run development server: `fastapi dev main.py`
5. View docs at `http://127.0.0.1:8000/docs`
6. Add endpoints in `main.py`

### Building a Database-Backed API

1. Create CRUD project: `python scripts/create_project.py crud my-api`
2. Set up PostgreSQL database
3. Configure `.env` with database credentials
4. Run to initialize database: `fastapi dev main.py`
5. Test endpoints at `http://127.0.0.1:8000/docs`
6. Add new models in `app/models.py`
7. Add new routers in `app/routers/`

### Serving an ML Model

1. Create ML project: `python scripts/create_project.py ml my-ml-api`
2. Save your trained model to `models/` directory
3. Update `app/models/model_loader.py` to load your model
4. Define input/output schemas in `app/schemas.py`
5. Add prediction endpoint in `app/routers/predict.py`
6. Run: `fastapi dev main.py`

## Best Practices

### Project Structure

Follow the standard FastAPI structure:
```
project/
├── main.py              # Application entry point
├── app/
│   ├── core/           # Configuration, security
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic models
│   ├── routers/        # Endpoint definitions
│   └── services/       # Business logic
├── tests/              # Test files
└── requirements.txt
```

### Async/Await

Always use `async def` for endpoints that perform I/O:
- Database queries
- HTTP requests to external services
- File operations
- ML model inference (for I/O-bound preprocessing)

Use regular `def` for CPU-bound operations unless running in thread pool.

### Dependency Injection

Use FastAPI's dependency injection for:
- Database sessions: `db: AsyncSession = Depends(get_db)`
- HTTP clients: `client: httpx.AsyncClient = Depends(get_http_client)`
- Authentication: `user: User = Depends(get_current_user)`

### Error Handling

Use HTTPException for API errors:
```python
from fastapi import HTTPException

if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

### Response Models

Always specify response models for type safety and auto-docs:
```python
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    ...
```

## API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

No additional configuration needed!

## Development Commands

```bash
# Development with auto-reload
fastapi dev main.py

# Production
fastapi run main.py

# With custom host/port
uvicorn main:app --host 0.0.0.0 --port 8080

# With workers (production)
uvicorn main:app --workers 4
```

## Resources

- **scripts/create_project.py** - Project scaffolding tool
- **assets/** - Project templates (minimal, crud, microservice, ml)
- **references/crud-patterns.md** - Database and CRUD operation patterns
- **references/microservice-patterns.md** - Microservice architecture patterns
- **references/ml-api-patterns.md** - ML model serving patterns
