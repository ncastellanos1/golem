from pydantic import BaseModel
from typing import Optional

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
