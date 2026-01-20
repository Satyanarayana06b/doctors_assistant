import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "clinic"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "admin")
    }
    
    print(f"Attempting to connect to database '{db_config['database']}' as user '{db_config['user']}'...")
    
    try:
        return psycopg2.connect(**db_config)
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        print(f"Please ensure:")
        print(f"  1. PostgreSQL is running")
        print(f"  2. Database '{db_config['database']}' exists")
        print(f"  3. User '{db_config['user']}' exists with correct password")
        raise