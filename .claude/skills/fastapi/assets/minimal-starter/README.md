# Minimal FastAPI Starter

A simple hello world FastAPI application to get started quickly.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
# Development mode with auto-reload
fastapi dev main.py

# Or using uvicorn directly
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints

- `GET /` - Hello world message
- `GET /health` - Health check
- `GET /items/{item_id}` - Example with path and query parameters
- `POST /echo` - Echo back a message
