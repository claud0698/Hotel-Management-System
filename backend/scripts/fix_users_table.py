"""
Fix users table - make email nullable
"""

import sqlite3

def fix_users_table():
    """Make email column nullable in users table"""
    conn = sqlite3.connect('kos.db')
    cursor = conn.cursor()

    try:
        # Create new table with email as nullable
        cursor.execute('''
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(120),
                created_at DATETIME
            )
        ''')

        # Copy data from old table to new table
        cursor.execute('''
            INSERT INTO users_new (id, username, password_hash, email, created_at)
            SELECT id, username, password_hash, email, created_at
            FROM users
        ''')

        # Drop old table
        cursor.execute('DROP TABLE users')

        # Rename new table
        cursor.execute('ALTER TABLE users_new RENAME TO users')

        # Create index
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)')

        conn.commit()
        print("✓ Successfully fixed users table (email is now nullable)")

    except Exception as e:
        print(f"Error fixing users table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_users_table()
