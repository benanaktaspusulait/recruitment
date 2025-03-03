from pydantic import BaseModel, Field
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class DatabaseConfig(BaseModel):
    DRIVER: str = "postgresql+psycopg2"
    HOST: str = Field(default="localhost", env="DB_HOST")
    PORT: int = Field(default=3306, env="DB_PORT")
    USERNAME: str = Field(default="root", env="DB_USER")
    PASSWORD: str = Field(default="", env="DB_PASSWORD")
    DATABASE: str = Field(default="recruitment", env="DB_NAME")
    SSL_MODE: str = Field(default="require", env="DB_SSL_MODE")
    SSL_CA: Optional[str] = Field(default=None, env="DB_SSL_CA")
    POOL_SIZE: int = Field(default=5, env="DB_POOL_SIZE")
    MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    POOL_RECYCLE: int = Field(default=1800, env="DB_POOL_RECYCLE")
    ECHO: bool = Field(default=False, env="DB_ECHO")

    def get_connection_url(self) -> str:
        if os.getenv("ENVIRONMENT") == "development":
            return "sqlite:///./recruitment.db"
        # Azure PostgreSQL connection string
        params = {
            "host": self.HOST,
            "port": self.PORT,
            "dbname": self.DATABASE,
            "user": self.USERNAME,
            "password": self.PASSWORD,
            "sslmode": self.SSL_MODE,
        }
        
        if self.SSL_CA:
            params["sslcert"] = self.SSL_CA
        
        return f"{self.DRIVER}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}?" + \
               "&".join(f"{key}={value}" for key, value in params.items() if value is not None)

class Settings(BaseModel):
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Azure Settings
    AZURE_INSIGHTS_CONNECTION_STRING: Optional[str] = Field(
        default=None,
        env="AZURE_INSIGHTS_CONNECTION_STRING"
    )

    # Database
    db: DatabaseConfig = DatabaseConfig()
    DATABASE_URL: str = Field(default="")

    # JWT Settings
    SECRET_KEY: str = Field(
        default="your-secret-key-here",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Email Settings
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="your-email@gmail.com", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="your-app-password", env="SMTP_PASSWORD")
    FROM_EMAIL: str = Field(default="recruitment@yourcompany.com", env="FROM_EMAIL")

    # Application Settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.DATABASE_URL = self.db.get_connection_url()

@lru_cache()
def get_settings() -> Settings:
    return Settings() 