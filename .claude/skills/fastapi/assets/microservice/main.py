"""
FastAPI Microservice Template
Demonstrates service-oriented architecture with external integrations.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx

from app.routers import products, orders
from app.core.config import settings


# Global HTTP client
http_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global http_client
    # Startup: Create HTTP client
    http_client = httpx.AsyncClient()
    yield
    # Shutdown: Close HTTP client
    await http_client.aclose()


app = FastAPI(
    title=settings.project_name,
    description="Microservice with external integrations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.project_name,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def get_http_client() -> httpx.AsyncClient:
    """Get the global HTTP client."""
    return http_client
