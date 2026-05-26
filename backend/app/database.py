from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI

# Instancia global de la conexión
client = None
db = None

def get_database():
    global client, db
    if db is None:
        client = AsyncIOMotorClient(MONGO_URI)
        # Obtener el nombre de la base de datos desde la URI (ej. portalProductos)
        db_name = MONGO_URI.split("/")[-1].split("?")[0]
        if not db_name:
            db_name = "portalProductos"
        db = client[db_name]
    return db

def close_database():
    global client, db
    if client is not None:
        client.close()
        client = None
        db = None
