#!/usr/bin/env python3
"""
Supabase Database Setup Verification Script
Checks connectivity and provides setup instructions
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def verify_env_file():
    """Verify .env file exists and has required variables"""
    print("=" * 70)
    print("CHECKING ENVIRONMENT CONFIGURATION")
    print("=" * 70)

    required_vars = [
        'DATABASE_URL',
        'DB_HOST',
        'DB_PORT',
        'DB_NAME',
        'DB_USER',
        'SUPABASE_URL',
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'KEY' in var or 'SECRET' in var:
                display = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display = value
            print(f"✓ {var}: {display}")
        else:
            print(f"✗ {var}: MISSING")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        return False

    print("\n✓ All environment variables are present!")
    return True

def verify_database_connection():
    """Verify database connection"""
    print("\n" + "=" * 70)
    print("CHECKING DATABASE CONNECTION")
    print("=" * 70)

    try:
        from sqlalchemy import create_engine, text

        database_url = os.getenv('DATABASE_URL')
        print(f"Database URL: {database_url.split('@')[0]}...@{database_url.split('@')[1]}")

        engine = create_engine(database_url, echo=False)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            return True

    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify Supabase project is running")
        print("2. Check DATABASE_URL in .env file")
        print("3. Ensure your IP address is whitelisted in Supabase")
        return False

def check_migration_file():
    """Check if migration file exists"""
    print("\n" + "=" * 70)
    print("CHECKING MIGRATION FILE")
    print("=" * 70)

    migration_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'migrations',
        '001_v1_0_initial_schema.sql'
    )

    if os.path.exists(migration_path):
        file_size = os.path.getsize(migration_path)
        print(f"✓ Migration file found: {migration_path}")
        print(f"  File size: {file_size:,} bytes")

        # Count tables
        with open(migration_path, 'r') as f:
            content = f.read()
            table_count = content.count('CREATE TABLE IF NOT EXISTS')
            print(f"  Tables to create: {table_count}")
        return True
    else:
        print(f"✗ Migration file not found: {migration_path}")
        return False

def check_models():
    """Check if models.py exists and can be imported"""
    print("\n" + "=" * 70)
    print("CHECKING MODELS")
    print("=" * 70)

    try:
        # Add backend to path
        backend_path = os.path.dirname(__file__)
        if backend_path not in sys.path:
            sys.path.insert(0, os.path.dirname(backend_path))

        from models import (
            Base, User, RoomType, Room, RoomImage, RoomTypeImage,
            Guest, Reservation, Payment, PaymentAttachment,
            Setting, Discount, BookingChannel
        )

        models = [
            User, RoomType, Room, RoomImage, RoomTypeImage,
            Guest, Reservation, Payment, PaymentAttachment,
            Setting, Discount, BookingChannel
        ]

        print(f"✓ All {len(models)} models imported successfully!")
        for model in models:
            print(f"  - {model.__tablename__}")

        return True
    except ImportError as e:
        print(f"✗ Failed to import models: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error loading models: {str(e)}")
        return False

def print_next_steps():
    """Print next steps"""
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)

    print("""
1. **Execute Migration in Supabase**:
   - Go to: https://supabase.com/dashboard
   - Select your project
   - Go to SQL Editor
   - Create new query
   - Copy and paste content from: backend/migrations/001_v1_0_initial_schema.sql
   - Click "Run" to execute all tables
   - Verify all tables were created

2. **Test Database Connection**:
   cd /path/to/project
   python -m backend.scripts.setup_supabase

3. **Install Backend Dependencies** (if not already done):
   pip install -r backend/requirements.txt

4. **Initialize Admin User**:
   python backend/init_admin.py

5. **Start Backend Server**:
   cd backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000

6. **Verify API is Running**:
   - API Docs: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/health
    """)

def main():
    """Run all checks"""
    print("\n" + "🏨 HOTEL MANAGEMENT SYSTEM - SUPABASE SETUP VERIFICATION" + "\n")

    checks = [
        ("Environment Variables", verify_env_file),
        ("Migration File", check_migration_file),
        ("Models", check_models),
        ("Database Connection", verify_database_connection),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {str(e)}")
            results[name] = False

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✓ All checks passed! Your setup is ready.")
        print_next_steps()
    else:
        print("\n❌ Some checks failed. Please review the errors above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
