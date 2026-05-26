from fastapi import APIRouter, Depends
from ..middleware.auth import get_current_user, require_role
from ..schemas.user import UpdateRoleRequest
from ..services.user_service import get_users, get_user, change_user_role, remove_user

router = APIRouter()

@router.get("")
async def list_users(current_user: dict = Depends(require_role("admin"))):
    return await get_users()

@router.get("/{user_id}")
async def get_user_by_id(user_id: str, current_user: dict = Depends(require_role("admin"))):
    return await get_user(user_id)

@router.put("/{user_id}/role")
async def update_role(
    user_id: str,
    body: UpdateRoleRequest,
    current_user: dict = Depends(require_role("admin"))
):
    return await change_user_role(user_id, body.role)

@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(require_role("admin"))):
    return await remove_user(user_id)
