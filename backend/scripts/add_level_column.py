"""
Migration script to add level column to rooms table
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kos.db')

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

def migrate():
    print("Adding 'level' column to rooms table...")

    with engine.connect() as connection:
        try:
            # Add level column with default value 'A'
            connection.execute(text("ALTER TABLE rooms ADD COLUMN level VARCHAR(10) DEFAULT 'A'"))
            connection.commit()
            print("✓ Successfully added 'level' column")

            # Update existing rooms based on room_number
            # If room number starts with 'A', set level to 'A'
            # If room number starts with 'B', set level to 'B'
            connection.execute(text("""
                UPDATE rooms
                SET level = CASE
                    WHEN room_number LIKE 'B%' THEN 'B'
                    ELSE 'A'
                END
            """))
            connection.commit()
            print("✓ Updated existing rooms with correct level values")

        except Exception as e:
            print(f"Error: {e}")
            print("Note: If column already exists, this is expected.")

if __name__ == '__main__':
    migrate()
    print("\nMigration complete!")
