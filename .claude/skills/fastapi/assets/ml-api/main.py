"""
FastAPI ML API Template
Demonstrates serving machine learning models with FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import predict
from app.models.model_loader import load_models, get_model

# Global model storage
models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Load ML models
    global models
    models = load_models()
    yield
    # Shutdown: cleanup if needed
    models.clear()


app = FastAPI(
    title="ML API",
    description="FastAPI application serving machine learning models",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router, prefix="/api/v1", tags=["predictions"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ML API",
        "version": "1.0.0",
        "models_loaded": list(models.keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": len(models)
    }


@app.get("/models")
async def list_models():
    """List all loaded models."""
    return {
        "models": list(models.keys())
    }
