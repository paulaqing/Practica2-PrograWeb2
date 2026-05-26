from bson import ObjectId
from fastapi import HTTPException, status
from ..models.user import get_user_by_username, update_user_cart
from ..models.product import get_product_by_id
from ..models import serialize_doc


async def get_cart(username: str):
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cart_items = user.get("cart", [])
    populated_cart = []
    total = 0.0

    for item in cart_items:
        product_id = str(item.get("product", ""))
        quantity = item.get("quantity", 1)
        product = await get_product_by_id(product_id)
        if product:
            subtotal = product["price"] * quantity
            total += subtotal
            populated_cart.append({
                "product": serialize_doc(product),
                "quantity": quantity,
                "subtotal": subtotal
            })

    return {"cart": populated_cart, "total": total}


async def add_to_cart(username: str, product_id: str, quantity: int = 1):
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cart = user.get("cart", [])
    found = False
    for item in cart:
        if str(item.get("product")) == product_id:
            item["quantity"] = item.get("quantity", 0) + quantity
            found = True
            break

    if not found:
        cart.append({"product": ObjectId(product_id), "quantity": quantity})

    await update_user_cart(username, cart)
    return {"message": "Producto añadido al carrito"}


async def update_cart_item(username: str, product_id: str, quantity: int):
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Cantidad no puede ser negativa")

    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cart = user.get("cart", [])
    item_found = False
    for item in cart:
        if str(item.get("product")) == product_id:
            item_found = True
            break

    if not item_found:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito")

    if quantity == 0:
        cart = [item for item in cart if str(item.get("product")) != product_id]
    else:
        for item in cart:
            if str(item.get("product")) == product_id:
                item["quantity"] = quantity
                break

    await update_user_cart(username, cart)
    return {"message": "Carrito actualizado"}


async def remove_from_cart(username: str, product_id: str):
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cart = user.get("cart", [])
    new_cart = [item for item in cart if str(item.get("product")) != product_id]
    await update_user_cart(username, new_cart)
    return {"message": "Producto eliminado del carrito"}


async def clear_cart(username: str):
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await update_user_cart(username, [])
    return {"message": "Carrito vaciado"}
