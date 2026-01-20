from db.connection import get_connection

try:
    conn = get_connection()
    print("✓ Connection successful!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✓ PostgreSQL version: {version[0]}")
    
    # Check if tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"✓ Tables found: {[t[0] for t in tables]}")
    
    cursor.close()
    conn.close()
    print("✓ Connection closed successfully")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
