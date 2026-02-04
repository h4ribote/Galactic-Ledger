from typing import Optional
from pydantic import BaseModel
from app.schemas.item import Item

class InventoryBase(BaseModel):
    quantity: int

class InventoryCreate(InventoryBase):
    item_id: int

class InventoryUpdate(BaseModel):
    quantity: int

class Inventory(InventoryBase):
    id: int
    planet_id: int
    item_id: int
    item: Optional[Item] = None

    class Config:
        from_attributes = True
