from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FleetBase(BaseModel):
    name: str

class FleetCreate(FleetBase):
    location_planet_id: int

class FleetUpdate(BaseModel):
    destination_planet_id: Optional[int] = None
    status: Optional[str] = None

class FleetResponse(FleetBase):
    id: int
    owner_id: int
    location_planet_id: Optional[int]
    destination_planet_id: Optional[int]
    arrival_time: Optional[datetime]
    status: str
    cargo_capacity: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
