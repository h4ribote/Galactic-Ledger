from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Galactic Ledger"
    API_V1_STR: str = "/api/v1"

    # Database
    # DATABASE_URL must be provided via environment variable or .env file
    DATABASE_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
