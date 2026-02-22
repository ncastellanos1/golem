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
    type: Optional[str] = None
    title: Optional[str] = None
    status: Optional[int] = None
    detail: Optional[str] = None
    instance: Optional[str] = None
    code: Optional[str] = None
    message: Optional[str] = None
