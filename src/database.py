from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings

# SQLite database URL
# You can change this to other databases like PostgreSQL if needed
settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Configure engine based on database type
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    connect_args["check_same_thread"] = False

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.drop_all(bind=engine)  # Drop all tables
    Base.metadata.create_all(bind=engine)  # Create all tables

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 