#!/usr/bin/env python3
"""
Create admin user directly using SQLAlchemy
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from passlib.context import CryptContext

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Database URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        hashed_password = pwd_context.hash('admin123')
        admin = User(
            username='admin',
            password_hash=hashed_password,
            email='admin@hotel.local',
            full_name='Administrator',
            role='admin',
            status='active'
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@hotel.local")
        print(f"   ID: {admin.id}")
        print(f"   Role: admin")
        print(f"   Status: active")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
