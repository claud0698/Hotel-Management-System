#!/usr/bin/env python3
"""
Update admin user password in PostgreSQL database
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Password hashing context (same as in models.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
    exit(1)

print(f"Connecting to database...")

# Create engine
engine = create_engine(DATABASE_URL)

# New credentials
username = 'admin'
new_password = 'admin123'
password_hash = pwd_context.hash(new_password)

try:
    with engine.connect() as conn:
        # Check if admin user exists
        result = conn.execute(
            text("SELECT id, username FROM users WHERE username = :username"),
            {"username": username}
        )
        user = result.fetchone()

        if user:
            print(f"Found user: {user[1]} (ID: {user[0]})")

            # Update password
            conn.execute(
                text("UPDATE users SET password_hash = :password_hash WHERE username = :username"),
                {"password_hash": password_hash, "username": username}
            )
            conn.commit()

            print(f"✅ Successfully updated password for user '{username}'")
            print(f"   New credentials:")
            print(f"   Username: {username}")
            print(f"   Password: {new_password}")
        else:
            # Create admin user if doesn't exist
            print(f"Admin user not found. Creating new admin user...")
            conn.execute(
                text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"),
                {"username": username, "password_hash": password_hash}
            )
            conn.commit()

            print(f"✅ Successfully created admin user")
            print(f"   Username: {username}")
            print(f"   Password: {new_password}")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n✅ Password update complete!")
print(f"You can now login with:")
print(f"  Username: admin")
print(f"  Password: admin123")
