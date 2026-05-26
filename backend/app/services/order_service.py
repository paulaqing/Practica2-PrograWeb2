from bson import ObjectId
from fastapi import HTTPException, status
from ..models.order import (
    get_all_orders as db_get_all,
    get_orders_by_user as db_get_by_user,
    get_order_by_id as db_get_by_id,
    create_order_in_db,
    update_order_status as db_update_status
)
from ..models.product import get_product_by_id
from ..models.user import get_user_by_username
from ..models import serialize_doc


def _serialize_order_with_user(order: dict, user_doc: dict = None) -> dict:
    """Serializa un pedido incluyendo el usuario como subdocumento compatible."""
    serialized = serialize_doc(order)
    if user_doc:
        serialized["user"] = {
            "id": str(user_doc.get("_id", "")),
            "_id": str(user_doc.get("_id", "")),
            "username": user_doc.get("username", "")
        }
    return serialized


async def get_all_orders(status_filter: str = None):
    orders = await db_get_all(status_filter)
    result = []
    for order in orders:
        # Poblar el campo user con username
        user_id = str(order.get("user", ""))
        from ..models.user import get_user_by_id
        user_doc = await get_user_by_id(user_id) if user_id else None
        result.append(_serialize_order_with_user(order, user_doc))
    return result


async def get_my_orders(username: str):
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    orders = await db_get_by_user(str(user["_id"]))
    result = []
    for order in orders:
        result.append(_serialize_order_with_user(order, user))
    return result


async def get_order(order_id: str, current_user: dict):
    order = await db_get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Solo el admin o el dueño pueden ver el pedido
    order_user_id = str(order.get("user", ""))
    if current_user.get("role") != "admin" and current_user.get("id") != order_user_id:
        raise HTTPException(status_code=403, detail="No autorizado")

    from ..models.user import get_user_by_id
    user_doc = await get_user_by_id(order_user_id)
    return _serialize_order_with_user(order, user_doc)


async def create_order(username: str, products_input: list):
    """
    products_input: lista de dicts con { productId, quantity }
    """
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    order_products = []
    total = 0.0

    for item in products_input:
        product_id = item.get("productId")
        quantity = item.get("quantity", 1)
        product = await get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

        subtotal = product["price"] * quantity
        total += subtotal
        order_products.append({
            "product": ObjectId(product_id),
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        })

    order_data = {
        "user": user["_id"],
        "products": order_products,
        "total": total,
        "status": "pending"
    }

    new_order = await create_order_in_db(order_data)
    return _serialize_order_with_user(new_order, user)


async def update_order_status(order_id: str, new_status: str):
    if new_status not in ["pending", "completed"]:
        raise HTTPException(status_code=400, detail="Estado inválido")

    updated = await db_update_status(order_id, new_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    order_user_id = str(updated.get("user", ""))
    from ..models.user import get_user_by_id
    user_doc = await get_user_by_id(order_user_id)
    return {"message": "Estado actualizado", "order": _serialize_order_with_user(updated, user_doc)}
