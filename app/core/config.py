# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    PMYSQL_URL: str = "mysql+pymysql://user:pass@localhost:3306/auth_db"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application settings
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Authentication Service"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()