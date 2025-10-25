"""
Update floor numbers based on room_number prefix
Floor 2 = A rooms (Atas/Upper)
Floor 1 = B rooms (Bawah/Lower)
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

def update_floors():
    print("Updating floor numbers based on room naming...")

    with engine.connect() as connection:
        try:
            # Update rooms starting with 'A' to floor 2
            # Update rooms starting with 'B' to floor 1
            connection.execute(text("""
                UPDATE rooms
                SET floor = CASE
                    WHEN room_number LIKE 'A%' THEN 2
                    WHEN room_number LIKE 'B%' THEN 1
                    ELSE floor
                END
            """))
            connection.commit()
            print("✓ Updated floor numbers:")
            print("  - A rooms → Floor 2 (Atas/Upper)")
            print("  - B rooms → Floor 1 (Bawah/Lower)")

            # Drop the level column if it exists
            try:
                connection.execute(text("ALTER TABLE rooms DROP COLUMN level"))
                connection.commit()
                print("✓ Removed 'level' column")
            except Exception as e:
                print(f"Note: Column 'level' may not exist or couldn't be dropped: {e}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    update_floors()
    print("\nMigration complete!")
