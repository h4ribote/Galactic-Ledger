import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.db.session import engine

# Setup logger
logger = logging.getLogger("uvicorn.info")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Verify DB connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful.")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(title="Galactic Ledger API", version="0.1.0", lifespan=lifespan)

# CORS Configuration
origins = [
    "http://localhost:3000",  # React Frontend
    "http://localhost:5173",  # Vite Dev Server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Galactic Ledger API"}

@app.get("/health")
async def health_check():
    # Check DB connection
    try:
        async with engine.connect() as conn:
             await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
