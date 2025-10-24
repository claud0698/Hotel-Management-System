"""
Database seeding script for Kos Management Dashboard
Creates sample data for testing and development
"""

from datetime import datetime, timedelta
from app import app, db
from models import User, Room, Tenant, Payment, Expense, RoomHistory


def seed_users():
    """Create sample user accounts."""
    print("Seeding users...")

    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("  - Admin user already exists, skipping")
        return

    admin = User(
        username='admin',
        email='admin@kos.local'
    )
    admin.set_password('admin123')

    db.session.add(admin)
    db.session.commit()
    print(f"  ✓ Created admin user (username: admin, password: admin123)")


def seed_rooms():
    """Create sample rooms."""
    print("Seeding rooms...")

    # Check if rooms exist
    existing = Room.query.count()
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
        db.session.add(room)

    db.session.commit()
    print(f"  ✓ Created {len(rooms_data)} sample rooms")


def seed_tenants():
    """Create sample tenants."""
    print("Seeding tenants...")

    # Check if tenants exist
    existing = Tenant.query.count()
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
        db.session.add(tenant)

    db.session.commit()
    print(f"  ✓ Created {len(tenants_data)} sample tenants")


def seed_room_history():
    """Create sample room history."""
    print("Seeding room history...")

    # Check if history exists
    existing = RoomHistory.query.count()
    if existing > 0:
        print(f"  - {existing} room history records already exist, skipping")
        return

    tenants = Tenant.query.filter(Tenant.current_room_id.isnot(None)).all()

    for tenant in tenants:
        history = RoomHistory(
            room_id=tenant.current_room_id,
            tenant_id=tenant.id,
            move_in_date=tenant.move_in_date or datetime.utcnow(),
        )
        db.session.add(history)

    db.session.commit()
    print(f"  ✓ Created {len(tenants)} room history records")


def seed_payments():
    """Create sample payments."""
    print("Seeding payments...")

    # Check if payments exist
    existing = Payment.query.count()
    if existing > 0:
        print(f"  - {existing} payments already exist, skipping")
        return

    tenants = Tenant.query.filter(Tenant.current_room_id.isnot(None)).all()
    today = datetime.utcnow()

    payment_count = 0

    for tenant in tenants:
        # Get tenant's room rate
        room = Room.query.get(tenant.current_room_id)
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
            db.session.add(payment)
            payment_count += 1

    db.session.commit()
    print(f"  ✓ Created {payment_count} sample payments")


def seed_expenses():
    """Create sample expenses."""
    print("Seeding expenses...")

    # Check if expenses exist
    existing = Expense.query.count()
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
        db.session.add(expense)

    db.session.commit()
    print(f"  ✓ Created {len(expenses_data)} sample expenses")


def clear_database():
    """Clear all data from database."""
    print("\n⚠️  Clearing all data from database...")

    # Delete in order of dependencies
    db.session.query(Payment).delete()
    db.session.query(RoomHistory).delete()
    db.session.query(Tenant).delete()
    db.session.query(Room).delete()
    db.session.query(User).delete()
    db.session.query(Expense).delete()

    db.session.commit()
    print("  ✓ Database cleared")


def seed_database():
    """Seed database with sample data."""
    print("\n" + "=" * 60)
    print("DATABASE SEEDING")
    print("=" * 60 + "\n")

    with app.app_context():
        seed_users()
        seed_rooms()
        seed_tenants()
        seed_room_history()
        seed_payments()
        seed_expenses()

        print("\n" + "=" * 60)
        print("✓ Database seeding complete!")
        print("=" * 60)
        print("\nTest Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nYou can now start the server with: python app.py")
        print("")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        with app.app_context():
            clear_database()
            seed_database()
    else:
        seed_database()
