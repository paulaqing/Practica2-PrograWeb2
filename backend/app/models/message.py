from datetime import datetime
from ..database import get_database

def get_messages_collection():
    return get_database()["messages"]

async def get_room_messages(room: str, limit: int = 50):
    col = get_messages_collection()
    cursor = col.find({"room": room}).sort("timestamp", -1).limit(limit)
    messages = await cursor.to_list(length=None)
    # Devolver ordenados cronológicamente (de más antiguo a más reciente)
    return messages[::-1]

async def save_message(room: str, sender: str, message: str):
    col = get_messages_collection()
    doc = {
        "room": room,
        "sender": sender,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    result = await col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc

async def cleanup_messages(room: str, max_messages: int = 50):
    col = get_messages_collection()
    count = await col.count_documents({"room": room})
    if count > max_messages:
        cursor = col.find({"room": room}).sort("timestamp", 1).limit(count - max_messages)
        to_delete = await cursor.to_list(length=None)
        ids = [msg["_id"] for msg in to_delete]
        if ids:
            await col.delete_many({"_id": {"$in": ids}})
