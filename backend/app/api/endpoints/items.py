from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.item import Item
from app.schemas.item import Item as ItemSchema, ItemCreate

router = APIRouter()

@router.get("/", response_model=List[ItemSchema])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Retrieve items.
    """
    result = await db.execute(select(Item).offset(skip).limit(limit))
    items = result.scalars().all()
    return items

@router.post("/", response_model=ItemSchema)
async def create_item(
    item_in: ItemCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Create new item.
    """
    item = Item(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
