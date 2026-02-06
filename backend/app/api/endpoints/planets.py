from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.planet import Planet
from app.models.inventory import Inventory
from app.models.item import Item
from app.schemas.planet import Planet as PlanetSchema
from app.schemas.inventory import Inventory as InventorySchema, InventoryCreate

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

from app.models.user import User

@router.get("/{planet_id}/inventory", response_model=List[InventorySchema])
async def read_planet_inventory(
    planet_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get inventory of a planet for the current user.
    """
    # Check if planet exists
    result = await db.execute(select(Planet).where(Planet.id == planet_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Planet not found")

    result = await db.execute(
        select(Inventory)
        .where(Inventory.planet_id == planet_id)
        .where(Inventory.user_id == current_user.id)
        .options(joinedload(Inventory.item))
    )
    inventory = result.scalars().all()
    return inventory

@router.post("/{planet_id}/inventory", response_model=InventorySchema)
async def add_planet_inventory(
    planet_id: int,
    inventory_in: InventoryCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add item to planet inventory (or update quantity) for the current user.
    """
    # Check if planet exists
    result = await db.execute(select(Planet).where(Planet.id == planet_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Planet not found")

    # Check if item exists
    result = await db.execute(select(Item).where(Item.id == inventory_in.item_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if inventory entry already exists
    result = await db.execute(
        select(Inventory)
        .where(Inventory.planet_id == planet_id)
        .where(Inventory.item_id == inventory_in.item_id)
        .where(Inventory.user_id == current_user.id)
        .options(joinedload(Inventory.item))
    )
    inventory_item = result.scalar_one_or_none()

    if inventory_item:
        new_quantity = inventory_item.quantity + inventory_in.quantity
        if new_quantity < 0:
             raise HTTPException(status_code=400, detail="Insufficient inventory quantity")
        inventory_item.quantity = new_quantity
    else:
        if inventory_in.quantity < 0:
             raise HTTPException(status_code=400, detail="Cannot create inventory with negative quantity")
        inventory_item = Inventory(
            user_id=current_user.id,
            planet_id=planet_id,
            item_id=inventory_in.item_id,
            quantity=inventory_in.quantity
        )
        db.add(inventory_item)

    await db.commit()
    await db.refresh(inventory_item)

    # Reload with item relationship for response
    result = await db.execute(
        select(Inventory)
        .where(Inventory.id == inventory_item.id)
        .options(joinedload(Inventory.item))
    )
    return result.scalar_one()
