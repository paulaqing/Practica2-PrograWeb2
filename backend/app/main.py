import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import get_database, close_database
from .chat_sio import socket_app

# Importar routers modulares
from .routers import auth, products, cart, users, orders, graphql

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Controlador de ciclo de vida de la aplicación.
    Inicializa la conexión con MongoDB al iniciar y la cierra al apagar.
    """
    # Conectar base de datos
    db = get_database()
    print("Conexion establecida con MongoDB de forma asincrona")
    yield
    # Desconectar base de datos
    close_database()
    print("Conexion de MongoDB cerrada")

# Crear aplicación FastAPI con gestor de ciclo de vida
app = FastAPI(
    title="Portal de Productos y Cafetería - Práctica 2",
    description="Backend completo en Python con FastAPI y arquitectura limpia.",
    version="1.0.0",
    lifespan=lifespan
)

# ====== Configuración de Middleware Global (CORS) ======
# Permitir peticiones desde cualquier origen (especialmente útil para desarrollo local y proxies de Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== Registro de Rutas REST & GraphQL ======
# auth.router está montado en / porque el proxy de Vite '/api/auth/login' se reescribe como '/login'
app.include_router(auth.router, tags=["Authentication"])

# Los demás routers se montan bajo sus prefijos de API correspondientes
app.include_router(products.router, prefix="/api/products", tags=["Products CRUD"])
app.include_router(cart.router, prefix="/api/cart", tags=["Shopping Cart"])
app.include_router(users.router, prefix="/api/users", tags=["Users Management"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders Management"])

# graphql.router está montado en la raíz porque expone directamente el endpoint '/graphql'
app.include_router(graphql.router, tags=["GraphQL Endpoints"])

# ====== Servidor de Archivos Estáticos (Imágenes de Productos) ======
# Se localiza la carpeta public del backend original para compatibilidad con las imágenes guardadas
ROOT_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = ROOT_DIR / "src" / "public" / "uploads"

# Asegurar que el directorio de imágenes físicas existe
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Montar los directorios para servir imágenes estáticas tanto en '/uploads' como en '/api/uploads'
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/api/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="api_uploads")

# ====== Servidor de Chat en Tiempo Real ======
# Montar la aplicación ASGI del servidor Socket.io de chat en la ruta '/socket.io'
app.mount("/socket.io", socket_app)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Servidor backend de la Práctica 2 en Python activo y listo.",
        "framework": "FastAPI",
        "version": "1.0.0"
    }
