from pydantic import BaseModel, Field

class UpdateOrderStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(pending|completed)$")
