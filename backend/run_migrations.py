#!/usr/bin/env python3
"""
Database migration runner for Supabase
Executes SQL migration files against the database
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

def run_migrations():
    """Run all SQL migration files in order"""
    migrations_dir = Path(__file__).parent / 'migrations'
    migration_files = sorted(migrations_dir.glob('*.sql'))

    if not migration_files:
        print("No migration files found")
        return

    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        for migration_file in migration_files:
            print(f"\nRunning: {migration_file.name}")
            print("-" * 60)

            with open(migration_file, 'r') as f:
                sql = f.read()

            try:
                # Handle PostgreSQL procedural blocks (DO $$ ... $$;)
                # Split by $$ to separate blocks, then recombine properly
                import re

                # First, handle DO blocks specially
                do_blocks = re.findall(r'DO\s*\$\$[\s\S]*?\$\$\s*;', sql, re.IGNORECASE)
                for block in do_blocks:
                    if block.strip():
                        connection.execute(text(block))

                # Remove DO blocks from sql for normal statement processing
                remaining_sql = sql
                for block in do_blocks:
                    remaining_sql = remaining_sql.replace(block, '')

                # Split remaining by ; to handle multiple statements
                statements = [s.strip() for s in remaining_sql.split(';') if s.strip()]
                for statement in statements:
                    # Skip comment-only statements
                    if statement and not statement.startswith('--'):
                        connection.execute(text(statement))

                connection.commit()
                print(f"✓ {migration_file.name} completed successfully")
            except Exception as e:
                print(f"✗ Error in {migration_file.name}: {e}")
                connection.rollback()
                raise

if __name__ == '__main__':
    try:
        run_migrations()
        print("\n" + "=" * 60)
        print("All migrations completed successfully!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"Migration failed: {e}")
        print("=" * 60)
        sys.exit(1)
