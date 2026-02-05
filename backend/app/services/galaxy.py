import random
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.planet import Planet

logger = logging.getLogger(__name__)

PLANET_NAMES_PREFIX = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
    "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
    "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega", "Kepler",
    "Gliese", "Trappist", "Proxima", "Sirius", "Vega", "Altair", "Deneb"
]
PLANET_NAMES_SUFFIX = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "Prime", "Major", "Minor", "B", "C", "d"]

async def initialize_galaxy(db: AsyncSession, planet_count: int = 100):
    """
    Initializes the galaxy with random planets if none exist.
    """
    try:
        # Check if planets exist
        result = await db.execute(select(func.count(Planet.id)))
        count = result.scalar()

        if count > 0:
            logger.info(f"Galaxy already initialized with {count} planets.")
            return

        logger.info(f"Initializing galaxy with {planet_count} planets...")

        planets_to_create = []
        for _ in range(planet_count):
            name_base = random.choice(PLANET_NAMES_PREFIX)
            if random.random() > 0.5:
                 name = f"{name_base}-{random.randint(10, 999)}"
            else:
                 name = f"{name_base} {random.choice(PLANET_NAMES_SUFFIX)}"

            planet = Planet(
                name=name,
                x=int(random.uniform(-1000, 1000) * 1000),
                y=int(random.uniform(-1000, 1000) * 1000),
                slots=random.randint(3, 12),
                temperature=int(random.uniform(-150, 150) * 1000),
                gravity=int(random.uniform(0.3, 2.5) * 1000),
            )
            planets_to_create.append(planet)

        db.add_all(planets_to_create)
        await db.commit()
        logger.info("Galaxy initialization complete.")

    except Exception as e:
        logger.error(f"Error initializing galaxy: {e}")
        await db.rollback()
        raise
