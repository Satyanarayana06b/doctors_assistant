import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# First, connect to postgres database as superuser to create user and database
postgres_password = input("Enter your PostgreSQL 'postgres' user password: ")

try:
    # Connect to default postgres database
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password=postgres_password
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if user admin exists
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='admin'")
    if cursor.fetchone():
        print("✓ User 'admin' already exists")
    else:
        cursor.execute("CREATE USER admin WITH PASSWORD 'admin'")
        print("✓ Created user 'admin'")
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='clinic'")
    if cursor.fetchone():
        print("✓ Database 'clinic' already exists")
    else:
        cursor.execute("CREATE DATABASE clinic OWNER admin")
        print("✓ Created database 'clinic'")
    
    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE clinic TO admin")
    print("✓ Granted privileges to admin")
    
    cursor.close()
    conn.close()
    
    # Now connect to clinic database as admin to create schema
    print("\nConnecting to clinic database to create tables...")
    conn = psycopg2.connect(
        host="localhost",
        database="clinic",
        user="admin",
        password="admin"
    )
    cursor = conn.cursor()
    
    # Read and execute schema.sql
    with open('db/schema.sql', 'r') as f:
        schema_sql = f.read()
        # Split by CREATE statements and execute separately
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        for statement in statements:
            if statement:
                cursor.execute(statement)
        print("✓ Created tables")
    
    # Read and execute seed.sql
    with open('db/seed.sql', 'r') as f:
        seed_sql = f.read()
        statements = [s.strip() for s in seed_sql.split(';') if s.strip()]
        for statement in statements:
            if statement:
                cursor.execute(statement)
        print("✓ Inserted seed data")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Database setup completed successfully!")
    print("You can now run: python test_db_connection.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease ensure PostgreSQL is running and you have the correct postgres password.")
