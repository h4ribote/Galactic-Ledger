from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.planet import Planet
from app.schemas.planet import Planet as PlanetSchema

router = APIRouter()

@router.get("/", response_model=List[PlanetSchema])
async def read_planets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Retrieve planets.
    """
    result = await db.execute(select(Planet).offset(skip).limit(limit))
    planets = result.scalars().all()
    return planets

@router.get("/{planet_id}", response_model=PlanetSchema)
async def read_planet(
    planet_id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get planet by ID.
    """
    result = await db.execute(select(Planet).where(Planet.id == planet_id))
    planet = result.scalar_one_or_none()
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")
    return planet
