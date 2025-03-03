from src.database import init_db, SessionLocal
from src.database.seed import seed_database

def reset_and_seed():
    print("Resetting database...")
    init_db()
    
    print("Seeding database...")
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed() 