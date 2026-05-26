from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from ..middleware.auth import get_current_user, require_role
from ..services.product_service import (
    get_products,
    create_new_product,
    update_existing_product,
    delete_existing_product
)

router = APIRouter()

@router.get("")
async def list_products(current_user: dict = Depends(get_current_user)):
    return await get_products()

@router.post("", status_code=201)
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    stock: int = Form(0),
    isActive: str = Form("true"),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_role("admin"))
):
    is_active_bool = isActive.lower() == "true" if isinstance(isActive, str) else bool(isActive)
    return await create_new_product(
        name=name,
        price=price,
        description=description,
        stock=stock,
        isActive=is_active_bool,
        file=image
    )

@router.put("/{product_id}")
async def update_product(
    product_id: str,
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    stock: Optional[int] = Form(None),
    isActive: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: dict = Depends(require_role("admin"))
):
    is_active_bool = None
    if isActive is not None:
        is_active_bool = isActive.lower() == "true"
    return await update_existing_product(
        product_id=product_id,
        name=name,
        price=price,
        description=description,
        stock=stock,
        isActive=is_active_bool,
        file=image
    )

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    return await delete_existing_product(product_id)
