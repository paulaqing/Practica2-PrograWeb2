from bson import ObjectId
from datetime import datetime
from ..database import get_database

def get_products_collection():
    return get_database()["products"]

async def get_all_products():
    col = get_products_collection()
    cursor = col.find().sort("createdAt", -1)
    return await cursor.to_list(length=None)

async def get_product_by_id(product_id: str):
    if not ObjectId.is_valid(product_id):
        return None
    col = get_products_collection()
    return await col.find_one({"_id": ObjectId(product_id)})

async def create_product(product_data: dict):
    col = get_products_collection()
    product_data["createdAt"] = datetime.utcnow()
    product_data["updatedAt"] = datetime.utcnow()
    result = await col.insert_one(product_data)
    product_data["_id"] = result.inserted_id
    return product_data

async def update_product(product_id: str, update_data: dict):
    if not ObjectId.is_valid(product_id):
        return None
    col = get_products_collection()
    update_data["updatedAt"] = datetime.utcnow()
    await col.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    return await get_product_by_id(product_id)

async def delete_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        return False
    col = get_products_collection()
    result = await col.delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count > 0
