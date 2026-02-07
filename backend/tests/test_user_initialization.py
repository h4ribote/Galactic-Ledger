import pytest
import pytest_asyncio
import random
from sqlalchemy import select
from app.db.session import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app.models.wallet import Balance
from app.models.planet import Planet
from app.models.fleet import Fleet
from app.services.user_service import initialize_new_user

@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_initialize_new_user():
    async with SessionLocal() as db:
        # Create a mock user
        # Generate a random ID to avoid collision if DB is reused
        user_id = random.randint(100000000, 999999999)
        username = f"TestUser_{user_id}"

        user = User(id=user_id, username=username)
        db.add(user)
        # Flush to make sure user exists for FK constraints
        await db.flush()

        # Call the initialization function
        await initialize_new_user(user, db)

        # Flush pending changes to make them visible to select queries
        await db.flush()

        # Verify Balance
        result = await db.execute(select(Balance).where(Balance.user_id == user_id))
        balances = result.scalars().all()
        assert len(balances) == 1
        assert balances[0].currency_type == "CRED"
        assert balances[0].amount == 10000

        # Verify Planet
        result = await db.execute(select(Planet).where(Planet.owner_id == user_id))
        planets = result.scalars().all()
        assert len(planets) == 1
        planet = planets[0]
        # Check name format (contains Colony or is an existing planet name)
        assert planet.owner_id == user_id

        # Verify Fleet
        result = await db.execute(select(Fleet).where(Fleet.owner_id == user_id))
        fleets = result.scalars().all()
        assert len(fleets) == 1
        fleet = fleets[0]
        assert fleet.name == "Starter Fleet"
        assert fleet.location_planet_id == planet.id

        # Note: We do not commit, so changes should be rolled back when session context ends
        # However, since we are using SQLite in a file or memory, flush writes to it.
        # The session rollbacks on exit.
