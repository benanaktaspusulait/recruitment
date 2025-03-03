from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings

settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Configure engine based on database type
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    connect_args["check_same_thread"] = False

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 