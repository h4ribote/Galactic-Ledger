import random
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.wallet import Balance
from app.models.planet import Planet
from app.models.fleet import Fleet

logger = logging.getLogger(__name__)

async def initialize_new_user(user: User, db: AsyncSession):
    """
    Initializes a new user with starting assets:
    1. 10,000 CRED
    2. A planet (either an existing unowned one or a newly created one)
    3. A starter fleet at that planet
    """
    logger.info(f"Initializing assets for new user {user.id} ({user.username})...")

    # 1. Grant initial funds (10,000 CRED)
    initial_credits = Balance(
        user_id=user.id,
        currency_type="CRED",
        amount=10000
    )
    db.add(initial_credits)

    # 2. Assign a planet
    # Try to find an unowned planet first
    # We might want to pick one that is not too far, but for now just any unowned planet
    result = await db.execute(select(Planet).where(Planet.owner_id == None).limit(1))
    planet = result.scalars().first()

    if planet:
        logger.info(f"Assigning existing unowned planet {planet.name} to user {user.id}")
        planet.owner_id = user.id
    else:
        # Create a new planet
        # Random coordinates between -100 and 100
        x = random.randint(-100, 100)
        y = random.randint(-100, 100)
        name_suffix = random.randint(1000, 9999)
        planet_name = f"Colony {name_suffix}"

        logger.info(f"Creating new planet {planet_name} at ({x}, {y}) for user {user.id}")
        planet = Planet(
            name=planet_name,
            x=x,
            y=y,
            slots=5,
            owner_id=user.id
        )
        db.add(planet)

    # Flush to ensure planet.id is available if it was just created
    await db.flush()

    # 3. Create a starter fleet
    fleet = Fleet(
        owner_id=user.id,
        name="Starter Fleet",
        location_planet_id=planet.id,
        status="IDLE"
    )
    db.add(fleet)

    logger.info(f"User {user.id} initialization complete.")
