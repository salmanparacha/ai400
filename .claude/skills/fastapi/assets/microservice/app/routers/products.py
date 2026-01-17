"""Product endpoints."""
from fastapi import APIRouter, Depends, HTTPException
import httpx

from app.schemas import Product
from main import get_http_client

router = APIRouter()

# Mock data for demo
PRODUCTS = [
    {"id": 1, "name": "Laptop", "description": "High-performance laptop", "price": 999.99, "stock": 10},
    {"id": 2, "name": "Mouse", "description": "Wireless mouse", "price": 29.99, "stock": 50},
    {"id": 3, "name": "Keyboard", "description": "Mechanical keyboard", "price": 79.99, "stock": 30},
]


@router.get("/", response_model=list[Product])
async def get_products():
    """Get all products."""
    return PRODUCTS


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a product by ID."""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
