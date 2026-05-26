from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timedelta
from ..config import JWT_SECRET

def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("authorization")
    print(f"DEBUG AUTH: Recibido header authorization: {auth_header}")
    if not auth_header or not auth_header.startswith("Bearer "):
        print("DEBUG AUTH: Token no proporcionado o formato incorrecto")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado"
        )
    token = auth_header.split(" ")[1]
    payload = verify_jwt_token(token)
    if payload is None:
        print(f"DEBUG AUTH: Token inválido o expirado. Token: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    print(f"DEBUG AUTH: Token verificado con éxito. Usuario: '{payload.get('username')}' (Rol: {payload.get('role')})")
    return payload

def require_role(allowed_role: str):
    async def dependency(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado"
            )
        return current_user
    return dependency
