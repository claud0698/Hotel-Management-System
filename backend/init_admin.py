#!/usr/bin/env python3
"""
Initialize Admin User
Creates default admin user if it doesn't exist
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from models import Base, User

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_admin():
    """Initialize admin user"""
    db = SessionLocal()

    try:
        # Check if admin exists
        admin = db.query(User).filter(User.username == 'admin').first()

        if admin:
            print("✅ Admin user already exists")
            print(f"   Username: {admin.username}")
            print(f"   Created: {admin.created_at}")
        else:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@kos.com'
            )
            admin.set_password('admin123')

            db.add(admin)
            db.commit()
            db.refresh(admin)

            print("✅ Admin user created successfully")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   ID: {admin.id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Admin User Initialization")
    print("=" * 60)
    print(f"\nDatabase: PostgreSQL (Supabase)\n")

    init_admin()

    print("\n" + "=" * 60)
