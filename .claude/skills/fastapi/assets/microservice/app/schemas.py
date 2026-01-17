"""Pydantic schemas."""
from pydantic import BaseModel
from datetime import datetime


class Product(BaseModel):
    """Product schema."""
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int


class OrderItem(BaseModel):
    """Order item schema."""
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    """Order creation schema."""
    customer_id: int
    items: list[OrderItem]


class Order(BaseModel):
    """Order response schema."""
    id: int
    customer_id: int
    items: list[OrderItem]
    total: float
    status: str
    created_at: datetime
