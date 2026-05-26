import asyncio
from datetime import datetime
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI

coffee_shop_products = [
    {
        "name": "Café Espresso",
        "description": "Café intenso y aromático preparado en máquina express.",
        "price": 1.50,
        "stock": 50,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Café Latte",
        "description": "Espresso con abundante leche caliente y una fina capa de espuma.",
        "price": 2.20,
        "stock": 40,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Cappuccino Clásico",
        "description": "Partes iguales de espresso, leche caliente y espuma de leche.",
        "price": 2.50,
        "stock": 35,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Galleta con Chips de Chocolate",
        "description": "Galleta horneada en casa, crujiente por fuera y suave por dentro con chips de chocolate belga.",
        "price": 1.80,
        "stock": 25,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Croissant de Mantequilla",
        "description": "Cruasán tradicional francés, hojaldrado y con un intenso sabor a mantequilla.",
        "price": 1.60,
        "stock": 30,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Croissant de Chocolate",
        "description": "Cruasán relleno de crema de cacao y avellanas.",
        "price": 2.00,
        "stock": 20,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Batido de Fresa Natural",
        "description": "Batido refrescante hecho con fresas frescas, helado de vainilla y leche.",
        "price": 3.50,
        "stock": 15,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Frappuccino de Caramelo",
        "description": "Bebida fría de café licuado con hielo, leche y sirope de caramelo, coronado con nata montada.",
        "price": 3.80,
        "stock": 20,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Crepe Nutella y Plátano",
        "description": "Crepe dulce rellena de auténtica Nutella y rodajas de plátano fresco.",
        "price": 4.50,
        "stock": 12,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    },
    {
        "name": "Tarta de Zanahoria (Porción)",
        "description": "Porción de bizcocho esponjoso de zanahoria con frosting de queso crema.",
        "price": 3.20,
        "stock": 10,
        "isActive": True,
        "image": "",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
]

async def seed():
    print(f"Conectando a MongoDB en {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI)
    
    # Obtener base de datos
    db_name = MONGO_URI.split("/")[-1].split("?")[0]
    if not db_name:
        db_name = "portalProductos"
    db = client[db_name]
    
    # 1. Sembrado de Productos
    print("Eliminando productos antiguos...")
    await db["products"].delete_many({})
    
    print(f"Insertando {len(coffee_shop_products)} productos de cafetería...")
    result = await db["products"].insert_many(coffee_shop_products)
    print(f"Productos sembrados con exito! ({len(result.inserted_ids)} productos creados)")
    
    # 2. Sembrado de Usuarios por Defecto para pruebas
    print("Eliminando usuarios antiguos con nombres 'admin' o 'invitado'...")
    await db["users"].delete_many({"username": {"$in": ["admin", "invitado"]}})
    
    print("Creando usuarios por defecto...")
    hashed_admin_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_user = {
        "username": "admin",
        "password": hashed_admin_password,
        "role": "admin",
        "cart": [],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    hashed_user_password = bcrypt.hashpw("invitado123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    regular_user = {
        "username": "invitado",
        "password": hashed_user_password,
        "role": "user",
        "cart": [],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    await db["users"].insert_one(admin_user)
    await db["users"].insert_one(regular_user)
    print("Usuarios de prueba creados exitosamente!")
    print("   Administrador: admin / admin123")
    print("   Usuario Normal: invitado / invitado123")
    
    client.close()
    print("Conexion cerrada. Sembrado completado!")

if __name__ == "__main__":
    asyncio.run(seed())
