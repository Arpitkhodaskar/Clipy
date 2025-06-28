from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str = "user"
    organization: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None