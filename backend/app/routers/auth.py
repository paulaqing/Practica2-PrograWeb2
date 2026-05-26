from fastapi import APIRouter
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from ..services.auth_service import register_user, login_user

router = APIRouter()

@router.post("/register")
async def register(body: RegisterRequest):
    return await register_user(body.username, body.password, body.role)

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    return await login_user(body.username, body.password)
