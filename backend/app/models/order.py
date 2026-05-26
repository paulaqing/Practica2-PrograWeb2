from bson import ObjectId
from datetime import datetime
from ..database import get_database

def get_orders_collection():
    return get_database()["orders"]

async def get_all_orders(status: str = None):
    col = get_orders_collection()
    query = {}
    if status:
        query["status"] = status
    cursor = col.find(query).sort("createdAt", -1)
    return await cursor.to_list(length=None)

async def get_orders_by_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        return []
    col = get_orders_collection()
    cursor = col.find({"user": ObjectId(user_id)}).sort("createdAt", -1)
    return await cursor.to_list(length=None)

async def get_order_by_id(order_id: str):
    if not ObjectId.is_valid(order_id):
        return None
    col = get_orders_collection()
    return await col.find_one({"_id": ObjectId(order_id)})

async def create_order_in_db(order_data: dict):
    col = get_orders_collection()
    order_data["createdAt"] = datetime.utcnow()
    order_data["updatedAt"] = datetime.utcnow()
    result = await col.insert_one(order_data)
    order_data["_id"] = result.inserted_id
    return order_data

async def update_order_status(order_id: str, status: str):
    if not ObjectId.is_valid(order_id):
        return None
    col = get_orders_collection()
    await col.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status, "updatedAt": datetime.utcnow()}}
    )
    return await get_order_by_id(order_id)
