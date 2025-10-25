"""
Migrate users table to remove email column
"""

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kos.db')
db_path = DATABASE_URL.replace('sqlite:///./', '').replace('sqlite:///', '')

def migrate_users_table():
    """Remove email column from users table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if email column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        has_email = any(col[1] == 'email' for col in columns)

        if not has_email:
            print("Email column already removed")
            return

        # SQLite doesn't support DROP COLUMN directly for older versions
        # We need to recreate the table

        # 1. Create new table without email
        cursor.execute('''
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME
            )
        ''')

        # 2. Copy data from old table to new table
        cursor.execute('''
            INSERT INTO users_new (id, username, password_hash, created_at)
            SELECT id, username, password_hash, created_at
            FROM users
        ''')

        # 3. Drop old table
        cursor.execute('DROP TABLE users')

        # 4. Rename new table to original name
        cursor.execute('ALTER TABLE users_new RENAME TO users')

        # 5. Create index on username
        cursor.execute('CREATE INDEX IF NOT EXISTS ix_users_username ON users (username)')

        conn.commit()
        print("✓ Successfully migrated users table (removed email column)")

    except Exception as e:
        print(f"Error migrating users table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_users_table()
