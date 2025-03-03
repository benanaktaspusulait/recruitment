from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings
from sqlalchemy.pool import QueuePool
import ssl

settings = get_settings()

# Configure engine based on environment
if settings.ENVIRONMENT == "development":
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Production Azure PostgreSQL configuration
    connect_args = {}
    
    if settings.db.SSL_MODE == "require":
        connect_args["ssl"] = {
            "ssl_cert": settings.db.SSL_CA,
            "ssl_mode": settings.db.SSL_MODE
        }

    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.db.POOL_SIZE,
        max_overflow=settings.db.MAX_OVERFLOW,
        pool_timeout=settings.db.POOL_TIMEOUT,
        pool_recycle=settings.db.POOL_RECYCLE,
        echo=settings.db.ECHO,
        connect_args=connect_args
    )

    # Add ping/reconnect functionality
    @event.listens_for(engine, "engine_connect")
    def ping_connection(connection, branch):
        if branch:
            return

        try:
            connection.scalar("SELECT 1::integer")
        except Exception:
            connection.connection.close()
            raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 