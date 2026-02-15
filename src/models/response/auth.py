from typing import Optional
from pydantic import BaseModel

class UserDTO(BaseModel):
    id: str
    username: str
    email: str
    created_at: str

class AuthResponse(BaseModel):
    access_token: str
    expires_in: int
    user: UserDTO

class ErrorResponse(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
