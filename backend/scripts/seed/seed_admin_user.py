"""
Create initial admin user for the system
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from dotenv import load_dotenv

load_dotenv()

# Database configuration - force local SQLite
DATABASE_URL = 'sqlite:///./kos.db'

# Create engine and session
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin_user():
    """Create admin user if it doesn't exist"""
    db = SessionLocal()

    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.username == "admin").first()

        if admin:
            print("Admin user already exists")
            return

        # Create new admin user
        admin = User(username="admin")
        admin.set_password("admin123")  # Default password - should be changed

        db.add(admin)
        db.commit()

        print("✓ Admin user created successfully")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Please change the password after first login!")

    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Create admin user
    create_admin_user()
