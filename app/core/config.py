# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DB_HOST: str = "195.35.45.118"
    DB_PORT: str = "3306"
    DB_USER: str = "devflow"
    DB_PASSWORD: str = "Devflow2025"
    DB_NAME: str = "auth_db"
    TEST_DB_PATH: str = "./test_auth.db"
    
    # Construct the MySQL URL from components
    @property
    def PMYSQL_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SQLALCHEMY_TEST_DATABASE_URL(self) -> str:
        return f"sqlite:////{self.TEST_DB_PATH}"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # Application settings
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Authentication Service"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()