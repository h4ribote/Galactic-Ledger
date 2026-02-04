from typing import Optional
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    tier: int = 1
    volume: float = 1.0

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
