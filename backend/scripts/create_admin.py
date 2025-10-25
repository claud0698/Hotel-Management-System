#!/usr/bin/env python3
"""
Create admin user in database (works with SQLite, PostgreSQL, Supabase)
Usage: python3 create_admin.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not set in .env file")
    print("\nPlease create a .env file with:")
    print("DATABASE_URL=sqlite:///./kos.db")
    print("or")
    print("DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname")
    sys.exit(1)

print(f"🔌 Connecting to database...")
print(f"   Database: {'SQLite' if 'sqlite' in DATABASE_URL else 'PostgreSQL'}")

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        pool_pre_ping=True,
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    print("✅ Connected successfully!")

    # Create tables if they don't exist
    print("\n📋 Creating tables (if they don't exist)...")
    Base.metadata.create_all(engine)
    print("✅ Tables ready!")

    # Check if admin exists
    print("\n👤 Checking for existing admin user...")
    existing_admin = session.query(User).filter_by(username='admin').first()

    if existing_admin:
        print("⚠️  Admin user already exists!")
        print(f"   Username: {existing_admin.username}")
        print(f"   Email: {existing_admin.email}")
        print(f"   Created: {existing_admin.created_at}")

        response = input("\n❓ Do you want to reset the admin password? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            new_password = input("Enter new password (or press Enter for 'admin123'): ")
            if not new_password:
                new_password = 'admin123'

            existing_admin.set_password(new_password)
            session.commit()

            print(f"\n✅ Admin password updated successfully!")
            print(f"   Username: admin")
            print(f"   Password: {new_password}")
            print("\n⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("\n✅ No changes made.")
    else:
        # Create admin user
        print("\n🔨 Creating admin user...")

        username = input("Enter username (or press Enter for 'admin'): ")
        if not username:
            username = 'admin'

        email = input("Enter email (or press Enter for 'admin@kos-dashboard.com'): ")
        if not email:
            email = 'admin@kos-dashboard.com'

        password = input("Enter password (or press Enter for 'admin123'): ")
        if not password:
            password = 'admin123'

        admin = User(
            username=username,
            email=email
        )
        admin.set_password(password)

        session.add(admin)
        session.commit()

        print(f"\n✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print("\n⚠️  IMPORTANT: Change this password after first login!")

    session.close()

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check your DATABASE_URL in .env file")
    print("2. Make sure the database server is running")
    print("3. Verify network connectivity (for remote databases)")
    sys.exit(1)
