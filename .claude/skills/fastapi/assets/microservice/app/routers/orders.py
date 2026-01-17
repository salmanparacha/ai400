"""Order endpoints."""
from fastapi import APIRouter, Depends, HTTPException
import httpx
from datetime import datetime

from app.schemas import Order, OrderCreate
from app.services.inventory import check_stock, reserve_stock
from main import get_http_client

router = APIRouter()

# In-memory storage for demo
orders = []
order_counter = 1


@router.post("/", response_model=Order, status_code=201)
async def create_order(
    order_data: OrderCreate,
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """Create a new order with stock validation."""
    global order_counter

    # Validate stock for all items
    for item in order_data.items:
        has_stock = await check_stock(item.product_id, item.quantity, client)
        if not has_stock:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {item.product_id}"
            )

    # Reserve stock
    for item in order_data.items:
        await reserve_stock(item.product_id, item.quantity, client)

    # Calculate total (simplified)
    total = sum(item.quantity * 100.0 for item in order_data.items)

    # Create order
    order = Order(
        id=order_counter,
        customer_id=order_data.customer_id,
        items=order_data.items,
        total=total,
        status="pending",
        created_at=datetime.utcnow()
    )
    orders.append(order)
    order_counter += 1

    return order


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """Get an order by ID."""
    order = next((o for o in orders if o.id == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
