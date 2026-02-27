from pydantic import BaseModel
from typing import Optional, List

class PromptOverrideModel(BaseModel):
    id: str
    user_id: str
    prompt_key: str
    template: str
    created_at: str
    updated_at: str

class ListPromptOverridesResponse(BaseModel):
    data: Optional[List[PromptOverrideModel]] = None

class CategoryModel(BaseModel):
    id: str
    name: str

class TransactionModel(BaseModel):
    id: str
    user_id: str
    category_id: Optional[str] = None
    name: str
    amount: float
    date: str
    description: str
    created_at: str
    updated_at: str
    category: Optional[CategoryModel] = None

class TransactionResponseModel(BaseModel):
    data: TransactionModel

# Request Models
class BasePromptRequest(BaseModel):
    key: str
    template: str

class PromptOverrideRequest(BaseModel):
    template: str

class FeedbackRequest(BaseModel):
    usage_id: str
    rating: int
    comment: Optional[str] = None

class TransactionAIPayloadRequest(BaseModel):
    description: str

class RegisterUserRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginUserRequest(BaseModel):
    email: str
    password: str
