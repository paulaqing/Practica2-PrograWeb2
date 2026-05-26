import re
from fastapi import APIRouter, Request, HTTPException
from ..middleware.auth import verify_jwt_token
from ..services.user_service import get_users, change_user_role, remove_user
from ..services.order_service import create_order

router = APIRouter()


def _extract_token(request: Request) -> dict:
    """Extrae y verifica el token JWT de la petición."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return verify_jwt_token(token)


def _require_auth(user: dict):
    if user is None:
        raise HTTPException(status_code=401, detail="No autenticado")


def _require_admin(user: dict):
    _require_auth(user)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")


def _detect_operation(query: str) -> str:
    """Detecta qué operación GraphQL se está ejecutando."""
    q = query.strip().lower().replace("\n", " ").replace("\r", " ")
    q = re.sub(r'\s+', ' ', q)

    if re.search(r'mutation\s+\w*\s*\(?[^)]*\)?\s*\{?\s*createorder', q):
        return "createOrder"
    if re.search(r'mutation\s+\w*\s*\(?[^)]*\)?\s*\{?\s*updateuserrole', q):
        return "updateUserRole"
    if re.search(r'mutation\s+\w*\s*\(?[^)]*\)?\s*\{?\s*deleteuser', q):
        return "deleteUser"
    if re.search(r'query\s*\{?\s*users', q) or re.search(r'{\s*users', q):
        return "users"
    return "unknown"


@router.post("/graphql")
async def graphql_endpoint(request: Request):
    """
    Endpoint GraphQL ligero que maneja las operaciones usadas por el frontend Svelte.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Cuerpo de petición inválido")

    query = body.get("query", "")
    variables = body.get("variables") or {}

    current_user = _extract_token(request)
    operation = _detect_operation(query)

    # ─── QUERY: users ────────────────────────────────────────────────────────
    if operation == "users":
        _require_admin(current_user)
        try:
            users_list = await get_users()
            # Asegurar que los campos son los que espera el frontend
            normalized = []
            for u in users_list:
                normalized.append({
                    "id": u.get("id") or u.get("_id", ""),
                    "username": u.get("username", ""),
                    "role": u.get("role", "user"),
                    "createdAt": u.get("createdAt")
                })
            return {"data": {"users": normalized}}
        except HTTPException as e:
            return {"errors": [{"message": e.detail}]}

    # ─── MUTATION: updateUserRole ────────────────────────────────────────────
    elif operation == "updateUserRole":
        _require_admin(current_user)
        user_id = variables.get("id")
        role = variables.get("role")
        if not user_id or not role:
            return {"errors": [{"message": "Faltan parámetros: id y role son requeridos"}]}
        try:
            result = await change_user_role(user_id, role)
            user_doc = result.get("user", {})
            return {
                "data": {
                    "updateUserRole": {
                        "id": user_doc.get("id") or user_doc.get("_id", ""),
                        "role": user_doc.get("role", role)
                    }
                }
            }
        except HTTPException as e:
            return {"errors": [{"message": e.detail}]}

    # ─── MUTATION: deleteUser ────────────────────────────────────────────────
    elif operation == "deleteUser":
        _require_admin(current_user)
        user_id = variables.get("id")
        if not user_id:
            return {"errors": [{"message": "Falta parámetro: id es requerido"}]}
        try:
            await remove_user(user_id)
            return {"data": {"deleteUser": {"success": True, "message": "Usuario eliminado correctamente"}}}
        except HTTPException as e:
            return {"data": {"deleteUser": {"success": False, "message": e.detail}}}

    # ─── MUTATION: createOrder ───────────────────────────────────────────────
    elif operation == "createOrder":
        _require_auth(current_user)
        products_input = variables.get("products", [])
        if not products_input:
            return {"errors": [{"message": "Se requiere al menos un producto"}]}
        try:
            order = await create_order(current_user["username"], products_input)
            return {
                "data": {
                    "createOrder": {
                        "id": order.get("id") or order.get("_id", ""),
                        "total": order.get("total", 0),
                        "status": order.get("status", "pending"),
                        "createdAt": order.get("createdAt")
                    }
                }
            }
        except HTTPException as e:
            return {"errors": [{"message": e.detail}]}

    # ─── OPERACIÓN DESCONOCIDA ───────────────────────────────────────────────
    else:
        return {"errors": [{"message": f"Operación GraphQL no reconocida"}]}
