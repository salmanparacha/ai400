"""Inventory service integration."""
import httpx
from app.core.config import settings


async def check_stock(product_id: int, quantity: int, client: httpx.AsyncClient) -> bool:
    """Check if product has sufficient stock."""
    try:
        response = await client.get(
            f"{settings.inventory_service_url}/api/v1/inventory/{product_id}",
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()
        return data.get("stock", 0) >= quantity
    except httpx.HTTPError:
        # Handle error - could log, return False, or raise
        return False


async def reserve_stock(product_id: int, quantity: int, client: httpx.AsyncClient) -> bool:
    """Reserve stock for an order."""
    try:
        response = await client.post(
            f"{settings.inventory_service_url}/api/v1/inventory/{product_id}/reserve",
            json={"quantity": quantity},
            timeout=5.0
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False
