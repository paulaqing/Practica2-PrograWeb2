import bcrypt
from ..models.user import get_user_by_username, create_user
from ..middleware.auth import create_jwt_token
from fastapi import HTTPException, status

async def register_user(username: str, password_raw: str, role: str = "user"):
    # Comprobar si el usuario existe
    existing = await get_user_by_username(username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario ya existe."
        )
    
    # Hash de la contraseña
    hashed_password = bcrypt.hashpw(password_raw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # El rol siempre debe ser 'user' al registrarse públicamente
    user_data = {
        "username": username,
        "password": hashed_password,
        "role": "user"
    }
    
    await create_user(user_data)
    return {"message": f"Usuario {username} registrado correctamente"}

async def login_user(username: str, password_raw: str):
    print(f"DEBUG LOGIN: Intentando login para usuario: '{username}'")
    user = await get_user_by_username(username)
    if not user:
        print(f"DEBUG LOGIN: Usuario '{username}' no encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no encontrado."
        )
        
    # Verificar contraseña usando bcrypt nativo de forma segura
    if not bcrypt.checkpw(password_raw.encode('utf-8'), user["password"].encode('utf-8')):
        print(f"DEBUG LOGIN: Contraseña incorrecta para usuario: '{username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta."
        )
        
    # Generar token JWT con id, username y role
    token = create_jwt_token({
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"]
    })
    print(f"DEBUG LOGIN: Login exitoso para '{username}'. Token generado: {token[:20]}...")
    return {"token": token}
