"""
Database seeding script for Kos Management Dashboard
Creates sample data for testing and development
"""

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from models import Base, User, Room, Tenant, Payment, Expense, RoomHistory

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kos.db')

# Create engine and session
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_users(db):
    """Create sample user accounts."""
    print("Seeding users...")

    # Check if admin user exists
    admin = db.query(User).filter(User.username == 'admin').first()
    if admin:
        print("  - Admin user already exists, skipping")
        return

    admin = User(
        username='admin',
        email='admin@kos.local'
    )
    admin.set_password('admin123')

    db.add(admin)
    db.commit()
    print(f"  ✓ Created admin user (username: admin, password: admin123)")


def seed_rooms(db):
    """Create sample rooms."""
    print("Seeding rooms...")

    # Check if rooms exist
    existing = db.query(Room).count()
    if existing > 0:
        print(f"  - {existing} rooms already exist, skipping")
        return

    rooms_data = [
        ('101', 1, 'single', 1500000, 'available', 'WiFi, AC, Shared Bathroom'),
        ('102', 1, 'single', 1500000, 'occupied', 'WiFi, AC, Shared Bathroom'),
        ('103', 1, 'double', 2000000, 'occupied', 'WiFi, AC, Private Bathroom'),
        ('201', 2, 'single', 1500000, 'available', 'WiFi, AC, Shared Bathroom'),
        ('202', 2, 'single', 1500000, 'occupied', 'WiFi, AC, Shared Bathroom'),
        ('203', 2, 'double', 2000000, 'available', 'WiFi, AC, Private Bathroom'),
        ('301', 3, 'suite', 2500000, 'occupied', 'WiFi, AC, Private Bathroom, Kitchen'),
        ('302', 3, 'single', 1500000, 'available', 'WiFi, AC, Shared Bathroom'),
        ('303', 3, 'single', 1500000, 'occupied', 'WiFi, AC, Shared Bathroom'),
        ('304', 3, 'double', 2000000, 'maintenance', 'WiFi, AC, Private Bathroom'),
    ]

    for room_num, floor, room_type, rate, status, amenities in rooms_data:
        room = Room(
            room_number=room_num,
            floor=floor,
            room_type=room_type,
            monthly_rate=rate,
            status=status,
            amenities=amenities
        )
        db.add(room)

    db.commit()
    print(f"  ✓ Created {len(rooms_data)} sample rooms")


def seed_tenants(db):
    """Create sample tenants."""
    print("Seeding tenants...")

    # Check if tenants exist
    existing = db.query(Tenant).count()
    if existing > 0:
        print(f"  - {existing} tenants already exist, skipping")
        return

    tenants_data = [
        ('Ahmad Malik', '0812345678', 'ahmad@email.com', '3172031234567890', 102, 'active'),
        ('Siti Nurhaliza', '0823456789', 'siti@email.com', '3172031234567891', 103, 'active'),
        ('Budi Santoso', '0834567890', 'budi@email.com', '3172031234567892', 202, 'active'),
        ('Dewi Lestari', '0845678901', 'dewi@email.com', '3172031234567893', 301, 'active'),
        ('Rini Wijaya', '0856789012', 'rini@email.com', '3172031234567894', 303, 'active'),
        ('Adi Gunawan', '0867890123', 'adi@email.com', '3172031234567895', None, 'inactive'),
    ]

    move_in_date = datetime.utcnow() - timedelta(days=90)

    for name, phone, email, id_num, room_id, status in tenants_data:
        tenant = Tenant(
            name=name,
            phone=phone,
            email=email,
            id_number=id_num,
            move_in_date=move_in_date if room_id else None,
            current_room_id=room_id,
            status=status,
            notes=f"Tenant {name} - Registered in database"
        )
        db.add(tenant)

    db.commit()
    print(f"  ✓ Created {len(tenants_data)} sample tenants")


def seed_room_history(db):
    """Create sample room history."""
    print("Seeding room history...")

    # Check if history exists
    existing = db.query(RoomHistory).count()
    if existing > 0:
        print(f"  - {existing} room history records already exist, skipping")
        return

    tenants = db.query(Tenant).filter(Tenant.current_room_id != None).all()

    for tenant in tenants:
        history = RoomHistory(
            room_id=tenant.current_room_id,
            tenant_id=tenant.id,
            move_in_date=tenant.move_in_date or datetime.utcnow(),
        )
        db.add(history)

    db.commit()
    print(f"  ✓ Created {len(tenants)} room history records")


def seed_payments(db):
    """Create sample payments."""
    print("Seeding payments...")

    # Check if payments exist
    existing = db.query(Payment).count()
    if existing > 0:
        print(f"  - {existing} payments already exist, skipping")
        return

    tenants = db.query(Tenant).filter(Tenant.current_room_id != None).all()
    today = datetime.utcnow()

    payment_count = 0

    for tenant in tenants:
        # Get tenant's room rate
        room = db.query(Room).filter(Room.id == tenant.current_room_id).first()
        if not room:
            continue

        # Create 3 months of payments
        for month_offset in range(-2, 1):
            if month_offset < 0:
                # Past payments (should be paid)
                due_date = today.replace(day=1) + timedelta(days=month_offset * 30)
                paid_date = due_date + timedelta(days=5)
                status = 'paid'
            else:
                # Current month payment
                due_date = today.replace(day=1)
                paid_date = None
                # 60% chance of being paid
                status = 'paid' if payment_count % 5 != 0 else 'pending'

            payment = Payment(
                tenant_id=tenant.id,
                amount=room.monthly_rate,
                due_date=due_date,
                paid_date=paid_date,
                status=status,
                payment_method='transfer' if status == 'paid' else None,
                receipt_number=f"RCP-{tenant.id}-{due_date.strftime('%Y%m')}" if status == 'paid' else None,
                notes=f"Monthly rent for {due_date.strftime('%B %Y')}"
            )
            db.add(payment)
            payment_count += 1

    db.commit()
    print(f"  ✓ Created {payment_count} sample payments")


def seed_expenses(db):
    """Create sample expenses."""
    print("Seeding expenses...")

    # Check if expenses exist
    existing = db.query(Expense).count()
    if existing > 0:
        print(f"  - {existing} expenses already exist, skipping")
        return

    expenses_data = [
        ('maintenance', 500000, 'Fixed broken AC in room 101'),
        ('utilities', 800000, 'Electricity bill for October'),
        ('utilities', 300000, 'Water bill for October'),
        ('supplies', 250000, 'Cleaning supplies and toilet papers'),
        ('maintenance', 350000, 'Repaired door lock in room 203'),
        ('cleaning', 400000, 'Monthly cleaning service'),
        ('supplies', 150000, 'Light bulbs and miscellaneous'),
        ('maintenance', 600000, 'Plumbing repair in bathroom'),
    ]

    today = datetime.utcnow()

    for category, amount, description in expenses_data:
        # Spread expenses over last 30 days
        expense_date = today - timedelta(days=15)

        expense = Expense(
            date=expense_date,
            category=category,
            amount=amount,
            description=description,
            receipt_url=None
        )
        db.add(expense)

    db.commit()
    print(f"  ✓ Created {len(expenses_data)} sample expenses")


def clear_database(db):
    """Clear all data from database."""
    print("\n⚠️  Clearing all data from database...")

    # Delete in order of dependencies
    db.query(Payment).delete()
    db.query(RoomHistory).delete()
    db.query(Tenant).delete()
    db.query(Room).delete()
    db.query(User).delete()
    db.query(Expense).delete()

    db.commit()
    print("  ✓ Database cleared")


def seed_database():
    """Seed database with sample data."""
    print("\n" + "=" * 60)
    print("DATABASE SEEDING")
    print("=" * 60 + "\n")

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_users(db)
        seed_rooms(db)
        seed_tenants(db)
        seed_room_history(db)
        seed_payments(db)
        seed_expenses(db)

        print("\n" + "=" * 60)
        print("✓ Database seeding complete!")
        print("=" * 60)
        print("\nTest Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nYou can now start the server with: python app.py")
        print("")
    finally:
        db.close()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            clear_database(db)
            seed_database()
        finally:
            db.close()
    else:
        seed_database()
