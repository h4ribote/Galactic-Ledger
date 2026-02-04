from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BuildingBase(BaseModel):
    type: str

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int
    planet_id: int
    status: str
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True
