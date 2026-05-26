from bson import ObjectId
from datetime import datetime
from ..database import get_database

def get_users_collection():
    return get_database()["users"]

async def get_user_by_username(username: str):
    col = get_users_collection()
    return await col.find_one({"username": username})

async def get_user_by_id(user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    col = get_users_collection()
    return await col.find_one({"_id": ObjectId(user_id)})

async def create_user(user_data: dict):
    col = get_users_collection()
    user_data["createdAt"] = datetime.utcnow()
    user_data["updatedAt"] = datetime.utcnow()
    user_data.setdefault("cart", [])
    user_data.setdefault("role", "user")
    result = await col.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data

async def update_user_role(user_id: str, role: str):
    if not ObjectId.is_valid(user_id):
        return None
    col = get_users_collection()
    await col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": role, "updatedAt": datetime.utcnow()}}
    )
    return await get_user_by_id(user_id)

async def delete_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        return False
    col = get_users_collection()
    result = await col.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

async def get_all_users():
    col = get_users_collection()
    cursor = col.find().sort("createdAt", -1)
    return await cursor.to_list(length=None)

async def update_user_cart(username: str, cart: list):
    col = get_users_collection()
    await col.update_one(
        {"username": username},
        {"$set": {"cart": cart, "updatedAt": datetime.utcnow()}}
    )
