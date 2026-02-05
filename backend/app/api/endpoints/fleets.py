from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta, timezone
import math

from app.api import deps
from app.models.user import User
from app.models.fleet import Fleet
from app.models.planet import Planet
from app.schemas.fleet import FleetCreate, FleetUpdate, FleetResponse

router = APIRouter()

@router.post("/", response_model=FleetResponse)
async def create_fleet(
    fleet_in: FleetCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    # Verify planet exists
    planet = await db.get(Planet, fleet_in.location_planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")

    fleet = Fleet(
        owner_id=current_user.id,
        name=fleet_in.name,
        location_planet_id=fleet_in.location_planet_id,
        status="IDLE"
    )
    db.add(fleet)
    await db.commit()
    await db.refresh(fleet)
    return fleet

@router.get("/", response_model=List[FleetResponse])
async def read_fleets(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    result = await db.execute(
        select(Fleet).where(Fleet.owner_id == current_user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/{id}/move", response_model=FleetResponse)
async def move_fleet(
    id: int,
    fleet_update: FleetUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    fleet = await db.get(Fleet, id)
    if not fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    if fleet.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if fleet.status != "IDLE":
        raise HTTPException(status_code=400, detail="Fleet is busy")

    dest_id = fleet_update.destination_planet_id
    if not dest_id:
        raise HTTPException(status_code=400, detail="Destination required")

    dest_planet = await db.get(Planet, dest_id)
    if not dest_planet:
        raise HTTPException(status_code=404, detail="Destination planet not found")

    current_planet = await db.get(Planet, fleet.location_planet_id)

    # Calculate distance
    dist = math.sqrt((dest_planet.x - current_planet.x)**2 + (dest_planet.y - current_planet.y)**2)
    speed = 50.0 # units per hour (example)
    hours = dist / speed

    # For testing purposes, if hours is very small or zero, make it minimal
    if hours < 0.01: hours = 0.01

    arrival = datetime.now(timezone.utc) + timedelta(hours=hours)

    fleet.destination_planet_id = dest_id
    fleet.arrival_time = arrival
    fleet.status = "TRANSIT"

    await db.commit()
    await db.refresh(fleet)
    return fleet

@router.post("/{id}/arrive", response_model=FleetResponse)
async def process_arrival(
    id: int,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    fleet = await db.get(Fleet, id)
    if not fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")

    if fleet.status != "TRANSIT":
         raise HTTPException(status_code=400, detail="Fleet is not in transit")

    # Handle timezone awareness comparison
    now = datetime.now(timezone.utc)
    arrival = fleet.arrival_time
    if arrival and arrival.tzinfo is None:
        arrival = arrival.replace(tzinfo=timezone.utc)

    if arrival and now < arrival:
        raise HTTPException(status_code=400, detail="Fleet has not arrived yet")

    fleet.location_planet_id = fleet.destination_planet_id
    fleet.destination_planet_id = None
    fleet.arrival_time = None
    fleet.status = "IDLE"

    await db.commit()
    await db.refresh(fleet)
    return fleet
