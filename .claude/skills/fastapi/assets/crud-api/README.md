# FastAPI CRUD API with PostgreSQL

A production-ready FastAPI application with full CRUD operations and PostgreSQL database.

## Features

- Full CRUD operations for Users and Items
- PostgreSQL database with SQLAlchemy ORM
- Async/await support
- Password hashing with bcrypt
- Pydantic models for validation
- Automatic API documentation
- CORS middleware
- Environment-based configuration

## Project Structure

```
.
├── main.py                 # Application entry point
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection and session
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── routers/
│       ├── __init__.py
│       ├── users.py       # User endpoints
│       └── items.py       # Item endpoints
├── requirements.txt
└── .env.example

```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and create a database

3. Copy `.env.example` to `.env` and update with your database credentials:
```bash
cp .env.example .env
```

4. Update the `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/your_database
```

## Running

```bash
# Development mode with auto-reload
fastapi dev main.py

# Production mode
fastapi run main.py
```

The API will be available at `http://127.0.0.1:8000`

## API Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Users

- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{user_id}` - Get a user by ID
- `PATCH /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

### Items

- `POST /api/v1/items/` - Create a new item
- `GET /api/v1/items/` - Get all items
- `GET /api/v1/items/{item_id}` - Get an item by ID
- `PATCH /api/v1/items/{item_id}` - Update an item
- `DELETE /api/v1/items/{item_id}` - Delete an item

## Example Requests

### Create a User

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "secretpassword"
  }'
```

### Create an Item

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/items/?owner_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Item",
    "description": "This is a test item"
  }'
```
