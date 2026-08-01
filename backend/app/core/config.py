import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TerraVision AI"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_for_development_only_12345")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # DB Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./terravision.db")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()
