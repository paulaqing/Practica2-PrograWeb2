from pydantic import BaseModel, Field

class UpdateRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(user|admin)$")

class CartItemRequest(BaseModel):
    productId: str
    quantity: int = 1

class CartItemUpdateRequest(BaseModel):
    productId: str
    quantity: int
