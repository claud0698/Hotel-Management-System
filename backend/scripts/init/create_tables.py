#!/usr/bin/env python3
"""
Database table creation script using SQLAlchemy ORM
Creates all v1.0 tables from models.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Load environment variables
load_dotenv()

def create_tables():
    """Create all tables using SQLAlchemy"""
    try:
        print("\n" + "=" * 70)
        print("🏨 HOTEL MANAGEMENT SYSTEM - CREATE TABLES (SQLAlchemy)")
        print("=" * 70 + "\n")

        # Step 1: Check environment
        print("1. Checking environment configuration...")
        required_vars = ['DATABASE_URL']
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            print(f"   ❌ Missing environment variables: {', '.join(missing)}")
            print("   Make sure .env file exists in backend/ directory")
            return 1

        database_url = os.getenv('DATABASE_URL')
        # Mask sensitive parts
        masked_url = database_url.split('@')[0] + '...@' + database_url.split('@')[1] if '@' in database_url else database_url
        print(f"   ✓ Database URL configured: {masked_url}")

        # Step 2: Import models
        print("\n2. Importing models...")
        try:
            from models import (
                Base, User, RoomType, Room, RoomImage, RoomTypeImage,
                Guest, Reservation, Payment, PaymentAttachment,
                Setting, Discount, BookingChannel
            )
            print("   ✓ All models imported successfully")
        except ImportError as e:
            print(f"   ❌ Failed to import models: {str(e)}")
            return 1

        # Step 3: Create engine
        print("\n3. Creating database engine...")
        from sqlalchemy import create_engine, text, inspect

        try:
            engine = create_engine(
                database_url,
                connect_args={},
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=20,
                max_overflow=10,
                echo=False
            )
            print("   ✓ Engine created")
        except Exception as e:
            print(f"   ❌ Failed to create engine: {str(e)}")
            return 1

        # Step 4: Test connection
        print("\n4. Testing database connection...")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("   ✓ Connection successful")
        except Exception as e:
            print(f"   ❌ Connection failed: {str(e)}")
            return 1

        # Step 5: Create tables
        print("\n5. Creating tables...")
        try:
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())

            print(f"   Existing tables: {len(existing_tables)}")

            Base.metadata.create_all(bind=engine)

            # Re-check tables
            inspector = inspect(engine)
            new_tables = set(inspector.get_table_names())

            created_tables = new_tables - existing_tables

            print(f"\n   ✓ Tables created/verified: {len(new_tables)}")
            for table in sorted(new_tables):
                if table in created_tables:
                    print(f"     ✓ {table} (NEW)")
                else:
                    print(f"     • {table} (existing)")

        except Exception as e:
            print(f"   ❌ Failed to create tables: {str(e)}")
            return 1

        # Step 6: Verify indexes
        print("\n6. Verifying indexes...")
        try:
            inspector = inspect(engine)
            total_indexes = 0

            for table_name in inspector.get_table_names():
                indexes = inspector.get_indexes(table_name)
                total_indexes += len(indexes)

            print(f"   ✓ Indexes verified: {total_indexes} total")

        except Exception as e:
            print(f"   ⚠ Could not verify indexes: {str(e)}")

        # Summary
        print("\n" + "=" * 70)
        print("✓ Database tables created successfully!")
        print("=" * 70 + "\n")

        print("Next steps:")
        print("1. Seed initial data: python backend/scripts/seed_initial_data.py")
        print("2. Create admin user: python backend/init_admin.py")
        print("3. Start backend: cd backend && uvicorn app:app --reload")
        print("4. Access API: http://localhost:8000/api/docs")
        print()

        return 0

    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(create_tables())
