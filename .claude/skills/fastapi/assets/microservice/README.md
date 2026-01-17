# FastAPI Microservice Template

A microservice template demonstrating service-oriented architecture with external integrations.

## Features

- Service-oriented architecture
- External service integration with httpx
- Async HTTP client management
- Stock reservation pattern
- Environment-based configuration
- CORS support

## Project Structure

```
.
├── main.py                      # Application entry point
├── app/
│   ├── core/
│   │   └── config.py           # Configuration
│   ├── routers/
│   │   ├── products.py         # Product endpoints
│   │   └── orders.py           # Order endpoints
│   ├── services/
│   │   └── inventory.py        # Inventory service client
│   └── schemas.py              # Pydantic schemas
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
fastapi dev main.py
```

## API Endpoints

- `GET /api/v1/products/` - Get all products
- `GET /api/v1/products/{product_id}` - Get product by ID
- `POST /api/v1/orders/` - Create an order
- `GET /api/v1/orders/{order_id}` - Get order by ID

## Microservice Patterns

This template demonstrates:

1. **Service Integration**: External service calls with httpx
2. **Resource Management**: Proper lifecycle management for HTTP clients
3. **Error Handling**: Graceful handling of external service failures
4. **Validation**: Cross-service data validation (stock checks)
