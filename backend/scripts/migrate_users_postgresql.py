"""
Migrate users table in PostgreSQL to remove email column
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

def migrate_users_table():
    """Remove email column from users table in PostgreSQL"""
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("Not using PostgreSQL database")
        return

    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Check if email column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='users' AND column_name='email'
            """))

            if not result.fetchone():
                print("Email column already removed or doesn't exist")
                return

            # Drop the email column
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS email"))
            conn.commit()

            print("✓ Successfully removed email column from users table")

    except Exception as e:
        print(f"Error migrating users table: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    migrate_users_table()
