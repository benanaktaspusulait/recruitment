from sqlalchemy import inspect
from src.database import engine

def verify_schema():
    inspector = inspect(engine)
    
    # Check users table
    columns = inspector.get_columns('users')
    column_names = [c['name'] for c in columns]
    expected_columns = [
        'id', 'email', 'hashed_password', 'first_name', 'last_name',
        'role', 'is_active', 'created_at', 'updated_at',
        'created_by_id', 'updated_by_id'
    ]
    
    print("Users table columns:", column_names)
    missing = set(expected_columns) - set(column_names)
    if missing:
        print("Missing columns:", missing)
    else:
        print("Schema looks good!")

if __name__ == "__main__":
    verify_schema() 