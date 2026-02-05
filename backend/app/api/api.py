from fastapi import APIRouter
from app.api.endpoints import auth, users, planets, items, buildings, fleets, contracts

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(planets.router, prefix="/planets", tags=["planets"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(buildings.router, prefix="/planets", tags=["buildings"])
api_router.include_router(fleets.router, prefix="/fleets", tags=["fleets"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
