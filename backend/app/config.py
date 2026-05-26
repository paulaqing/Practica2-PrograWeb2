import os
from pathlib import Path

# Cargar archivo .env de forma manual
env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    # Quitar comillas si las tuviese
                    val = val.strip().strip("'").strip('"')
                    os.environ.setdefault(key.strip(), val)
    except Exception as e:
        print(f"⚠️ Error al cargar .env: {e}")

PORT = int(os.getenv("PORT", 3000))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/portalProductos")
JWT_SECRET = os.getenv("JWT_SECRET", "super_secreto_jwt")
