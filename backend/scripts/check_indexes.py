"""Check if database indexes exist"""
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Get inspector
inspector = inspect(engine)

# Check indexes for each table
tables = ['rooms', 'tenants', 'payments', 'expenses', 'room_history']

print("Checking Database Indexes\n")
print(f"Database: PostgreSQL (Supabase)\n")

for table in tables:
    print(f"Table: {table}")
    try:
        indexes = inspector.get_indexes(table)
        if indexes:
            for idx in indexes:
                cols = ', '.join(idx['column_names'])
                print(f"  - {idx['name']}: ({cols})")
        else:
            print("  - No indexes found")
    except Exception as e:
        print(f"  - Error: {e}")
    print()

# Check if tables exist
print("\nTables in Database:")
for table_name in inspector.get_table_names():
    print(f"  - {table_name}")
