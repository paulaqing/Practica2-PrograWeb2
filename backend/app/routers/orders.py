from fastapi import APIRouter, Depends, Query
from typing import Optional
from ..middleware.auth import get_current_user, require_role
from ..schemas.order import UpdateOrderStatusRequest
from ..services.order_service import (
    get_all_orders,
    get_my_orders,
    get_order,
    update_order_status
)

router = APIRouter()

@router.get("")
async def list_all_orders(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(require_role("admin"))
):
    return await get_all_orders(status)

@router.get("/my-orders")
async def my_orders(current_user: dict = Depends(get_current_user)):
    return await get_my_orders(current_user["username"])

@router.get("/{order_id}")
async def get_single_order(order_id: str, current_user: dict = Depends(get_current_user)):
    return await get_order(order_id, current_user)

@router.put("/{order_id}/status")
async def change_order_status(
    order_id: str,
    body: UpdateOrderStatusRequest,
    current_user: dict = Depends(require_role("admin"))
):
    return await update_order_status(order_id, body.status)
