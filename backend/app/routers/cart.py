from fastapi import APIRouter, Depends
from ..middleware.auth import get_current_user
from ..schemas.user import CartItemRequest, CartItemUpdateRequest
from ..services.cart_service import (
    get_cart,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart
)

router = APIRouter()

@router.get("")
async def get_my_cart(current_user: dict = Depends(get_current_user)):
    return await get_cart(current_user["username"])

@router.post("/add")
async def add_item(body: CartItemRequest, current_user: dict = Depends(get_current_user)):
    return await add_to_cart(current_user["username"], body.productId, body.quantity)

@router.put("/update")
async def update_item(body: CartItemUpdateRequest, current_user: dict = Depends(get_current_user)):
    return await update_cart_item(current_user["username"], body.productId, body.quantity)

@router.delete("/remove/{product_id}")
async def remove_item(product_id: str, current_user: dict = Depends(get_current_user)):
    return await remove_from_cart(current_user["username"], product_id)

@router.delete("/clear")
async def clear_my_cart(current_user: dict = Depends(get_current_user)):
    return await clear_cart(current_user["username"])
