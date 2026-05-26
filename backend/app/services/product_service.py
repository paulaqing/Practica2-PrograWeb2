import os
import time
import random
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from ..models.product import (
    get_all_products as db_get_all,
    get_product_by_id as db_get_by_id,
    create_product as db_create,
    update_product as db_update,
    delete_product as db_delete
)
from ..models import serialize_doc

# Definir la ruta física de uploads
ROOT_DIR = Path(__file__).resolve().parents[3]
UPLOADS_DIR = ROOT_DIR / "src" / "public" / "uploads"

# Asegurar que el directorio de uploads existe
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

async def save_uploaded_file(file: UploadFile) -> str:
    ext = Path(file.filename).suffix
    unique_suffix = f"{int(time.time() * 1000)}-{random.randint(1, 1000000000)}"
    new_filename = f"product-{unique_suffix}{ext}"
    dest_path = UPLOADS_DIR / new_filename
    
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return f"/uploads/{new_filename}"

def delete_physical_file(image_url: str):
    if not image_url:
        return
    filename = image_url.replace("/uploads/", "")
    file_path = UPLOADS_DIR / filename
    if file_path.exists() and file_path.is_file():
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"⚠️ Error al eliminar archivo físico {file_path}: {e}")

async def get_products():
    items = await db_get_all()
    return serialize_doc(items)

async def get_product(product_id: str):
    item = await db_get_by_id(product_id)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return serialize_doc(item)

async def create_new_product(
    name: str,
    price: float,
    description: str = "",
    stock: int = 0,
    isActive: bool = True,
    file: UploadFile = None
):
    image_path = ""
    if file:
        image_path = await save_uploaded_file(file)
        
    doc = {
        "name": name,
        "price": price,
        "description": description,
        "stock": stock,
        "isActive": isActive,
        "image": image_path
    }
    
    new_doc = await db_create(doc)
    return serialize_doc(new_doc)

async def update_existing_product(
    product_id: str,
    name: str = None,
    price: float = None,
    description: str = None,
    stock: int = None,
    isActive: bool = None,
    file: UploadFile = None
):
    product = await db_get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if price is not None:
        update_data["price"] = price
    if description is not None:
        update_data["description"] = description
    if stock is not None:
        update_data["stock"] = stock
    if isActive is not None:
        update_data["isActive"] = isActive
        
    if file:
        if product.get("image"):
            delete_physical_file(product["image"])
        new_image_path = await save_uploaded_file(file)
        update_data["image"] = new_image_path
        
    updated = await db_update(product_id, update_data)
    return serialize_doc(updated)

async def delete_existing_product(product_id: str):
    product = await db_get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    if product.get("image"):
        delete_physical_file(product["image"])
        
    await db_delete(product_id)
    return {"message": "Producto eliminado correctamente"}
