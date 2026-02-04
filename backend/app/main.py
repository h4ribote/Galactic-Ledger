from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Galactic Ledger API", version="0.1.0")

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
def health_check():
    return {"status": "healthy"}
