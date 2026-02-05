import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.building import Building
from app.models.inventory import Inventory
from app.models.item import Item
from app.core.game_data import BUILDINGS

logger = logging.getLogger(__name__)

async def _update_construction_status():
    async with SessionLocal() as session:
        now = datetime.now(timezone.utc)
        # Find buildings that are constructing and finished_at <= now
        query = select(Building).where(
            and_(
                Building.status == "constructing",
                Building.finished_at <= now
            )
        )
        result = await session.execute(query)
        buildings = result.scalars().all()

        count = 0
        for building in buildings:
            building.status = "active"
            session.add(building)
            count += 1

        if count > 0:
            await session.commit()
            logger.info(f"Updated status for {count} buildings to active.")

async def _produce_resources():
    async with SessionLocal() as session:
        # Get all active buildings
        query = select(Building).where(Building.status == "active")
        result = await session.execute(query)
        buildings = result.scalars().all()

        if not buildings:
            return

        # Cache items to avoid repeated queries
        items_cache = {} # {name: id}

        updates_count = 0

        for building in buildings:
            b_data = BUILDINGS.get(building.type)
            if not b_data or "production" not in b_data or not b_data["production"]:
                continue

            prod_info = b_data["production"]
            item_name = prod_info.get("item_name")
            rate = prod_info.get("rate_per_minute", 0)

            if not item_name or rate <= 0:
                continue

            # Resolve Item ID
            if item_name not in items_cache:
                item_res = await session.execute(select(Item).where(Item.name == item_name))
                item = item_res.scalars().first()
                if item:
                    items_cache[item_name] = item.id
                else:
                    logger.error(f"Item {item_name} not found in DB but required for production.")
                    continue

            item_id = items_cache[item_name]

            # Get or Create Inventory
            inv_query = select(Inventory).where(
                and_(Inventory.planet_id == building.planet_id, Inventory.item_id == item_id)
            )
            inv_res = await session.execute(inv_query)
            inventory = inv_res.scalars().first()

            if not inventory:
                inventory = Inventory(
                    planet_id=building.planet_id,
                    item_id=item_id,
                    quantity=0
                )
                session.add(inventory)

            inventory.quantity += rate
            session.add(inventory)
            updates_count += 1

        if updates_count > 0:
            await session.commit()
            logger.info(f"Production cycle complete. Updated {updates_count} inventories.")

@celery_app.task
def update_construction_status_task():
    try:
        asyncio.run(_update_construction_status())
    except Exception as e:
        logger.error(f"Error in update_construction_status_task: {e}")

@celery_app.task
def produce_resources_task():
    try:
        asyncio.run(_produce_resources())
    except Exception as e:
        logger.error(f"Error in produce_resources_task: {e}")
