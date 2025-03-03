import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import SessionLocal
from src.database.seed import seed_database
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed():
    logger.info("Starting database seed")
    db = SessionLocal()
    try:
        # Disable foreign key checks for SQLite
        db.execute(text("PRAGMA foreign_keys=OFF"))
        
        seed_database(db)
        
        # Re-enable foreign key checks
        db.execute(text("PRAGMA foreign_keys=ON"))
        
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed() 