#!/usr/bin/env python3
"""
Migrate data from SQLite to Supabase PostgreSQL
This script will:
1. Read all data from SQLite database
2. Create tables in Supabase
3. Copy all data to Supabase
"""

import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Base, User, Room, Tenant, RoomHistory, Payment, Expense
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def count_records(session, model):
    """Count records in a table"""
    return session.query(model).count()

def migrate_data():
    print_header("SQLite to Supabase Migration Tool")

    # SQLite connection
    sqlite_path = os.path.join(os.path.dirname(__file__), 'kos.db')
    if not os.path.exists(sqlite_path):
        print_error(f"SQLite database not found at: {sqlite_path}")
        print_info("Make sure kos.db exists in the backend directory")
        return False

    print_info(f"Source: SQLite database at {sqlite_path}")

    # Supabase connection from .env
    supabase_url = os.getenv('DATABASE_URL')
    if not supabase_url:
        print_error("DATABASE_URL not found in environment variables")
        print_info("Make sure .env file is configured with Supabase connection string")
        return False

    if 'sqlite' in supabase_url.lower():
        print_error("DATABASE_URL is still pointing to SQLite!")
        print_info("Update your .env file to use Supabase connection string")
        return False

    print_info(f"Target: Supabase PostgreSQL")
    print_info(f"Host: {supabase_url.split('@')[1].split(':')[0] if '@' in supabase_url else 'unknown'}")

    print("\n" + "-"*70 + "\n")

    # Confirm before proceeding
    print_warning("This will:")
    print("  1. Create all tables in Supabase (if they don't exist)")
    print("  2. Copy ALL data from SQLite to Supabase")
    print("  3. This will NOT delete existing Supabase data")
    print("  4. Duplicate records may be created if data already exists")

    response = input(f"\n{Colors.BOLD}Continue with migration? (yes/no): {Colors.ENDC}")
    if response.lower() not in ['yes', 'y']:
        print_info("Migration cancelled")
        return False

    try:
        # Create engines
        print_info("\nConnecting to databases...")
        sqlite_engine = create_engine(f'sqlite:///{sqlite_path}')
        supabase_engine = create_engine(supabase_url, pool_pre_ping=True)

        # Create sessions
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        SupabaseSession = sessionmaker(bind=supabase_engine)

        sqlite_session = SQLiteSession()
        supabase_session = SupabaseSession()

        print_success("Connected to SQLite")
        print_success("Connected to Supabase")

        # Create tables in Supabase
        print_info("\nCreating tables in Supabase...")
        Base.metadata.create_all(supabase_engine)
        print_success("Tables created/verified in Supabase")

        # Check what data exists
        print_info("\nAnalyzing SQLite data...")
        tables_to_migrate = [
            ('Users', User),
            ('Rooms', Room),
            ('Tenants', Tenant),
            ('Room History', RoomHistory),
            ('Payments', Payment),
            ('Expenses', Expense),
        ]

        migration_plan = []
        for table_name, model in tables_to_migrate:
            count = count_records(sqlite_session, model)
            if count > 0:
                migration_plan.append((table_name, model, count))
                print_info(f"  {table_name}: {count} records")
            else:
                print_warning(f"  {table_name}: 0 records (will skip)")

        if not migration_plan:
            print_warning("\nNo data found in SQLite database!")
            return True

        print(f"\n{Colors.BOLD}Total records to migrate: {sum(item[2] for item in migration_plan)}{Colors.ENDC}")

        response = input(f"\n{Colors.BOLD}Start migration? (yes/no): {Colors.ENDC}")
        if response.lower() not in ['yes', 'y']:
            print_info("Migration cancelled")
            return False

        # Migrate data
        print_header("Starting Data Migration")

        total_migrated = 0

        for table_name, model, count in migration_plan:
            print_info(f"\nMigrating {table_name}...")

            # Fetch all records from SQLite
            records = sqlite_session.query(model).all()

            migrated = 0
            skipped = 0
            errors = 0

            for record in records:
                try:
                    # Create a dictionary of the record
                    record_dict = {}
                    for column in record.__table__.columns:
                        value = getattr(record, column.name)
                        record_dict[column.name] = value

                    # Create new instance for Supabase
                    new_record = model(**record_dict)

                    # Add to Supabase session
                    supabase_session.add(new_record)
                    migrated += 1

                except Exception as e:
                    errors += 1
                    print_error(f"    Error migrating record ID {record.id}: {str(e)}")

            # Commit the batch
            try:
                supabase_session.commit()
                print_success(f"  Migrated {migrated} {table_name} records")
                if errors > 0:
                    print_warning(f"  Errors: {errors} records failed")
                total_migrated += migrated
            except Exception as e:
                supabase_session.rollback()
                print_error(f"  Failed to commit {table_name}: {str(e)}")

        # Verify migration
        print_header("Verifying Migration")

        for table_name, model, original_count in migration_plan:
            supabase_count = count_records(supabase_session, model)
            print_info(f"{table_name}:")
            print(f"  SQLite:   {original_count} records")
            print(f"  Supabase: {supabase_count} records")

            if supabase_count >= original_count:
                print_success(f"  ✓ Migration successful")
            else:
                print_warning(f"  ⚠ Count mismatch! Check for errors above")

        # Close sessions
        sqlite_session.close()
        supabase_session.close()

        print_header("Migration Complete!")
        print_success(f"Total records migrated: {total_migrated}")
        print_info("\nNext steps:")
        print("  1. Test your application with Supabase")
        print("  2. Verify data in Supabase dashboard")
        print("  3. Update your frontend to use the Supabase-backed API")
        print("  4. Deploy to Cloud Run when ready")

        return True

    except Exception as e:
        print_error(f"\nMigration failed: {str(e)}")
        import traceback
        print_error(traceback.format_exc())
        return False

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    try:
        success = migrate_data()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\nMigration cancelled by user")
        exit(1)
