#!/usr/bin/env python3
"""
Database initialization script - Executes Supabase migration SQL
Creates all v1.0 tables and initial data
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create connection to Supabase PostgreSQL"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return connection
    except psycopg2.Error as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        return None

def read_migration_file():
    """Read the SQL migration file"""
    migration_path = Path(__file__).parent.parent / 'migrations' / '001_v1_0_initial_schema.sql'

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return None

    try:
        with open(migration_path, 'r') as f:
            sql = f.read()
        return sql
    except Exception as e:
        print(f"❌ Failed to read migration file: {str(e)}")
        return None

def execute_migration(connection, sql):
    """Execute the migration SQL"""
    cursor = connection.cursor()

    try:
        # Split SQL into statements (simple approach)
        statements = sql.split(';')

        executed = 0
        skipped = 0
        errors = []

        for statement in statements:
            statement = statement.strip()

            # Skip empty statements and comments
            if not statement or statement.startswith('--'):
                continue

            try:
                cursor.execute(statement)
                executed += 1

                # Print progress for major operations
                if 'CREATE TABLE' in statement.upper():
                    table_name = statement.split()[3] if len(statement.split()) > 3 else 'table'
                    print(f"  ✓ Created table: {table_name}")
                elif 'INSERT INTO' in statement.upper():
                    print(f"  ✓ Inserted initial data")

            except psycopg2.Error as e:
                # Some errors are expected (e.g., duplicate tables with IF NOT EXISTS)
                if 'already exists' in str(e).lower() or 'conflict' in str(e).lower():
                    skipped += 1
                else:
                    errors.append(f"  ⚠ {str(e)}")

        connection.commit()
        return executed, skipped, errors

    except Exception as e:
        connection.rollback()
        print(f"❌ Migration failed: {str(e)}")
        return 0, 0, [str(e)]
    finally:
        cursor.close()

def verify_tables(connection):
    """Verify all tables were created"""
    cursor = connection.cursor()

    expected_tables = [
        'users', 'room_types', 'rooms', 'room_images', 'room_type_images',
        'guests', 'reservations', 'payments', 'payment_attachments',
        'settings', 'discounts', 'booking_channels'
    ]

    try:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        existing_tables = {row[0] for row in cursor.fetchall()}

        created = []
        missing = []

        for table in expected_tables:
            if table in existing_tables:
                created.append(table)
            else:
                missing.append(table)

        return created, missing

    except Exception as e:
        print(f"❌ Failed to verify tables: {str(e)}")
        return [], expected_tables
    finally:
        cursor.close()

def main():
    """Main execution"""
    print("\n" + "=" * 70)
    print("🏨 HOTEL MANAGEMENT SYSTEM - DATABASE INITIALIZATION")
    print("=" * 70 + "\n")

    # Step 1: Check environment
    print("1. Checking environment configuration...")
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print(f"   ❌ Missing environment variables: {', '.join(missing)}")
        print("   Make sure .env file exists in backend/ directory")
        return 1

    print(f"   ✓ Database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

    # Step 2: Connect to database
    print("\n2. Connecting to database...")
    connection = get_db_connection()

    if not connection:
        return 1

    print("   ✓ Connection successful")

    # Step 3: Read migration file
    print("\n3. Reading migration file...")
    sql = read_migration_file()

    if not sql:
        connection.close()
        return 1

    print(f"   ✓ Migration file loaded ({len(sql):,} bytes)")

    # Step 4: Execute migration
    print("\n4. Executing migration...")
    print("   Creating tables and initial data:\n")

    executed, skipped, errors = execute_migration(connection, sql)

    print(f"\n   Executed: {executed} statements")
    if skipped > 0:
        print(f"   Skipped: {skipped} statements (expected for IF NOT EXISTS)")

    if errors:
        print("\n   Errors encountered:")
        for error in errors:
            print(error)

    # Step 5: Verify tables
    print("\n5. Verifying tables...")
    created, missing = verify_tables(connection)

    print(f"   ✓ Created tables: {len(created)}/12")
    for table in created:
        print(f"     - {table}")

    if missing:
        print(f"\n   ⚠ Missing tables: {len(missing)}/12")
        for table in missing:
            print(f"     - {table}")

    # Cleanup
    connection.close()

    # Summary
    print("\n" + "=" * 70)
    if len(created) == 12 and not missing:
        print("✓ Database initialization COMPLETE!")
        print("=" * 70 + "\n")
        print("Next steps:")
        print("1. Create admin user: python backend/init_admin.py")
        print("2. Start backend: cd backend && uvicorn app:app --reload")
        print("3. Access API: http://localhost:8000/api/docs")
        return 0
    else:
        print("⚠ Database initialization completed with warnings")
        print("=" * 70 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
