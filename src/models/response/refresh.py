from typing import Optional
from pydantic import BaseModel

class RefreshResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "Bearer"
