from bson import ObjectId
from fastapi import HTTPException, status
from ..models.user import (
    get_all_users as db_get_all,
    get_user_by_id as db_get_by_id,
    update_user_role as db_update_role,
    delete_user as db_delete
)
from ..models import serialize_doc


async def get_users():
    users = await db_get_all()
    # Excluir password de la respuesta
    result = []
    for u in users:
        doc = serialize_doc(u)
        doc.pop("password", None)
        result.append(doc)
    return result


async def get_user(user_id: str):
    user = await db_get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    doc = serialize_doc(user)
    doc.pop("password", None)
    return doc


async def change_user_role(user_id: str, role: str):
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Rol inválido")
    updated = await db_update_role(user_id, role)
    if not updated:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    doc = serialize_doc(updated)
    doc.pop("password", None)
    return {"message": "Rol actualizado", "user": doc}


async def remove_user(user_id: str):
    success = await db_delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado correctamente"}
