from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.api import deps
from app.models.user import User
from app.models.planet import Planet
from app.models.wallet import Balance
from app.models.inventory import Inventory
from app.models.item import Item
from app.models.building import Building
from app.schemas import building as building_schema
from app.core.game_data import BUILDINGS
from app.api.endpoints.users import get_current_user

router = APIRouter()

@router.post("/{planet_id}/build", response_model=building_schema.Building)
async def build_structure(
    planet_id: int,
    building_in: building_schema.BuildingCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Check if planet exists and belongs to user
    result = await db.execute(select(Planet).where(Planet.id == planet_id))
    planet = result.scalars().first()
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")
    if planet.owner_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not your planet")

    # 2. Check building type validity
    b_type = building_in.type
    if b_type not in BUILDINGS:
        raise HTTPException(status_code=400, detail="Invalid building type")

    building_data = BUILDINGS[b_type]
    cost_currency = building_data.get("cost_currency", "CRED")
    cost_amount = Decimal(building_data.get("cost_amount", 0))
    cost_items = building_data.get("cost_items", {}) # dict { "ItemName": quantity }
    build_time = building_data["build_time_seconds"]

    # 3. Check Balance
    balance_result = await db.execute(select(Balance).where(
        Balance.user_id == current_user.id,
        Balance.currency_type == cost_currency
    ))
    balance = balance_result.scalars().first()

    if not balance or balance.amount < cost_amount:
         raise HTTPException(status_code=400, detail=f"Insufficient {cost_currency}")

    # 4. Check Inventory (Resources)
    item_names = list(cost_items.keys())
    items_map = {}
    if item_names:
        result = await db.execute(select(Item).where(Item.name.in_(item_names)))
        items_db = result.scalars().all()
        items_map = {item.name: item for item in items_db}

        for name in item_names:
            if name not in items_map:
                # Should we raise 500 or 400? If game data says Iron but DB has no Iron, it's a config error.
                raise HTTPException(status_code=500, detail=f"Game data error: Item {name} not found in DB")

        for name, qty in cost_items.items():
            item_id = items_map[name].id
            inv_result = await db.execute(select(Inventory).where(
                Inventory.planet_id == planet_id,
                Inventory.item_id == item_id
            ))
            inventory = inv_result.scalars().first()
            if not inventory or inventory.quantity < qty:
                raise HTTPException(status_code=400, detail=f"Insufficient {name}")

    # 5. Apply changes
    balance.amount -= cost_amount
    db.add(balance)

    if item_names:
        for name, qty in cost_items.items():
             item_id = items_map[name].id
             inv_result = await db.execute(select(Inventory).where(
                Inventory.planet_id == planet_id,
                Inventory.item_id == item_id
            ))
             inventory = inv_result.scalars().first()
             inventory.quantity -= qty
             db.add(inventory)

    # Create Building
    # Use UTC for timezone
    now = datetime.now(timezone.utc)
    finished_at = now + timedelta(seconds=build_time)

    new_building = Building(
        planet_id=planet_id,
        type=b_type,
        status="constructing",
        finished_at=finished_at
    )
    db.add(new_building)

    await db.commit()
    await db.refresh(new_building)

    return new_building

@router.get("/{planet_id}/buildings", response_model=List[building_schema.Building])
async def get_buildings(
    planet_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # Check planet existence
    result = await db.execute(select(Planet).where(Planet.id == planet_id))
    planet = result.scalars().first()
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")

    result = await db.execute(select(Building).where(Building.planet_id == planet_id))
    buildings = result.scalars().all()
    return buildings
