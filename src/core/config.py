from pydantic import BaseModel, Field
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseModel):
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./recruitment.db",
        env="DATABASE_URL"
    )

    # JWT Settings
    SECRET_KEY: str = Field(
        default="your-secret-key-here",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(
        default="HS256",
        env="ALGORITHM"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Email Settings
    SMTP_HOST: str = Field(
        default="smtp.gmail.com",
        env="SMTP_HOST"
    )
    SMTP_PORT: int = Field(
        default=587,
        env="SMTP_PORT"
    )
    SMTP_USER: str = Field(
        default="your-email@gmail.com",
        env="SMTP_USER"
    )
    SMTP_PASSWORD: str = Field(
        default="your-app-password",
        env="SMTP_PASSWORD"
    )
    FROM_EMAIL: str = Field(
        default="recruitment@yourcompany.com",
        env="FROM_EMAIL"
    )

    # Application Settings
    ENVIRONMENT: str = Field(
        default="development",
        env="ENVIRONMENT"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        env="LOG_LEVEL"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings() 