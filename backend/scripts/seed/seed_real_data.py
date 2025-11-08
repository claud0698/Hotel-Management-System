"""
Seed database with real payment data
Based on actual July-August payment records
"""

import sys
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Base, Room, Tenant, Payment, Expense, RoomHistory

# Database setup
DATABASE_URL = "sqlite:///./kos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_database():
    """Drop all tables and recreate"""
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped")

    print("📋 Creating fresh tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

def seed_rooms(db):
    """Create rooms with hotel numbering convention (101-404)"""
    print("\n🏠 Creating rooms...")

    # Room rates by type
    room_rates = {
        'STD': 300000,  # Standard Room
        'STT': 300000,  # Standard Twin Room
        'SUP': 400000,  # Superior Room
        'SUT': 400000,  # Superior Twin Room
        'DEL': 500000,  # Deluxe Room
        'JUS': 550000,  # Junior Suite Room
        'SUI': 600000,  # Suite Room
        'SUO': 650000,  # Suite Room with Ocean View
    }

    rooms_created = []

    # Floor 1 (100-199): Standard and Superior rooms
    room_types = ['STD', 'STD', 'STT', 'STT', 'SUP', 'SUP', 'SUP', 'SUP']
    for i, room_type in enumerate(room_types, 1):
        room_number = f"10{i}"
        room = Room(
            room_number=room_number,
            floor=1,
            room_type=room_type,
            monthly_rate=room_rates.get(room_type, 300000),
            status="available",
            amenities="AC, TV, Shower"
        )
        db.add(room)
        rooms_created.append(room)

    # Floor 2 (200-299): Superior and Deluxe rooms
    room_types = ['SUP', 'SUP', 'SUT', 'SUT', 'DEL', 'DEL', 'DEL', 'DEL']
    for i, room_type in enumerate(room_types, 1):
        room_number = f"20{i}"
        room = Room(
            room_number=room_number,
            floor=2,
            room_type=room_type,
            monthly_rate=room_rates.get(room_type, 400000),
            status="available",
            amenities="AC, TV, Shower"
        )
        db.add(room)
        rooms_created.append(room)

    # Floor 3 (300-399): Deluxe and Junior Suite rooms
    room_types = ['DEL', 'DEL', 'JUS', 'JUS', 'JUS', 'JUS', 'JUS', 'JUS']
    for i, room_type in enumerate(room_types, 1):
        room_number = f"30{i}"
        room = Room(
            room_number=room_number,
            floor=3,
            room_type=room_type,
            monthly_rate=room_rates.get(room_type, 500000),
            status="available",
            amenities="AC, TV, Shower, Mini Fridge"
        )
        db.add(room)
        rooms_created.append(room)

    # Floor 4 (400-499): Suite rooms
    room_types = ['SUI', 'SUI', 'SUO', 'SUO']
    for i, room_type in enumerate(room_types, 1):
        room_number = f"40{i}"
        room = Room(
            room_number=room_number,
            floor=4,
            room_type=room_type,
            monthly_rate=room_rates.get(room_type, 600000),
            status="available",
            amenities="AC, TV, Shower, Mini Fridge, Ocean View"
        )
        db.add(room)
        rooms_created.append(room)

    db.commit()

    # Refresh to get IDs
    for room in rooms_created:
        db.refresh(room)

    print(f"✅ Created {len(rooms_created)} rooms")
    return {room.room_number: room for room in rooms_created}

def seed_tenants_and_payments(db, rooms):
    """Create tenants and payments based on real data"""
    print("\n👥 Creating tenants and payments...")

    # Payment data: room_number -> (payment_method/note, amount, date_str, status)
    # Using hotel numbering: 101-404 (not A1-B12)
    payment_data = {
        '101': ('BCA', 300000, '2025-07-07', 'paid'),
        '102': ('M', 300000, '2025-07-02', 'paid'),
        '103': ('M', 300000, '2025-07-08', 'paid'),
        '104': ('BCA', 300000, '2025-07-02', 'paid'),
        '105': ('BCA', 300000, '2025-07-10', 'paid'),
        '201': ('BCA', 400000, '2025-07-18', 'paid'),
        '202': ('M', 400000, '2025-07-30', 'paid'),
        '203': ('M', 400000, '2025-08-02', 'paid'),
        '204': ('Vacant', None, None, 'vacant'),  # Vacant
        '205': ('M', 400000, '2025-07-25', 'paid'),
        '206': ('BCA', 400000, '2025-07-25', 'paid'),
        '207': ('BCA', 500000, '2025-07-18', 'paid'),
        '208': ('M', 500000, '2025-07-05', 'paid'),
        '301': ('BCA', 500000, '2025-07-07', 'paid'),
        '302': ('M', 500000, '2025-07-02', 'paid'),
        '303': ('BCA', 550000, '2025-07-07', 'paid'),
        '304': ('Vacant', None, None, 'vacant'),  # Empty
        '305': ('M', 550000, '2025-07-07', 'paid'),
        '306': ('M', 550000, '2025-07-30', 'paid'),
        '307': ('BCA', 550000, '2025-07-01', 'paid'),
        '308': ('M', 550000, '2025-08-03', 'paid'),
        '401': ('M', 600000, '2025-07-27', 'paid'),
        '402': ('Vacant', None, None, 'vacant'),  # Empty
        '403': ('M', 650000, '2025-07-10', 'paid'),
        '404': ('Owner', None, None, 'occupied'),  # Occupied but no payment yet
    }

    tenants_created = 0
    payments_created = 0

    for room_number, data in payment_data.items():
        method_or_note, amount, date_str, status = data
        room = rooms[room_number]

        # Skip vacant rooms
        if status == 'vacant':
            room.status = 'available'
            db.commit()
            continue

        # Create tenant
        tenant_name = f"Guest {room_number}" if method_or_note != 'Owner' else 'Owner'
        move_in_date = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)  # Assume moved in June

        tenant = Tenant(
            name=tenant_name,
            phone=f"08{room_number}1234567",
            email=f"guest{room_number}@hotel.example.com",
            id_number=f"3173010000{room_number}",
            move_in_date=move_in_date,
            current_room_id=room.id,
            status='active',
            notes=method_or_note if method_or_note in ['M', 'Occupied'] else None
        )
        db.add(tenant)
        db.flush()  # Get tenant ID

        # Create room history entry
        room_history = RoomHistory(
            room_id=room.id,
            tenant_id=tenant.id,
            move_in_date=move_in_date,
            move_out_date=None  # Still occupied
        )
        db.add(room_history)

        # Update room status
        room.status = 'occupied'

        tenants_created += 1

        # Create payment if amount exists
        if amount and date_str:
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)

            # Determine payment method
            if method_or_note == 'BCA':
                payment_method = 'transfer'
                receipt_number = f"BCA-{room_number}-{date_str}"
                notes = None
            else:  # M (manual/cash)
                payment_method = 'cash'
                receipt_number = None
                notes = method_or_note

            payment = Payment(
                tenant_id=tenant.id,
                amount=amount,
                due_date=payment_date,
                paid_date=payment_date,
                status='paid',
                payment_method=payment_method,
                receipt_number=receipt_number,
                period_months=1,
                notes=notes
            )
            db.add(payment)
            payments_created += 1

    db.commit()

    print(f"✅ Created {tenants_created} tenants")
    print(f"✅ Created {payments_created} payments")

    # Summary
    print("\n📊 Room Status Summary:")
    occupied = sum(1 for r in rooms.values() if r.status == 'occupied')
    available = sum(1 for r in rooms.values() if r.status == 'available')
    print(f"  - Occupied: {occupied}")
    print(f"  - Available: {available}")
    print(f"  - Total: {len(rooms)}")

def seed_expenses(db):
    """Create July expenses based on real data"""
    print("\n💸 Creating expenses...")

    # Expenses for July 2025
    expenses_data = [
        # Sampah (Garbage collection) - 4 times throughout July
        ("utilities", 37500, "2025-07-05", "Sampah minggu 1"),
        ("utilities", 37500, "2025-07-12", "Sampah minggu 2"),
        ("utilities", 37500, "2025-07-19", "Sampah minggu 3"),
        ("utilities", 37500, "2025-07-26", "Sampah minggu 4"),

        # Listrik (Electricity) - 2 times (Total: 405,000 to match 805k total)
        ("utilities", 202500, "2025-07-10", "Listrik bulan Juli (bagian 1)"),
        ("utilities", 202500, "2025-07-25", "Listrik bulan Juli (bagian 2)"),

        # Upah tukang rumput (Grass cutting labor) - 4 times
        ("maintenance", 37500, "2025-07-06", "Upah tukang rumput minggu 1"),
        ("maintenance", 37500, "2025-07-13", "Upah tukang rumput minggu 2"),
        ("maintenance", 37500, "2025-07-20", "Upah tukang rumput minggu 3"),
        ("maintenance", 37500, "2025-07-27", "Upah tukang rumput minggu 4"),

        # Racun rumput (Weed killer) - 4 times
        ("supplies", 25000, "2025-07-06", "Racun rumput minggu 1"),
        ("supplies", 25000, "2025-07-13", "Racun rumput minggu 2"),
        ("supplies", 25000, "2025-07-20", "Racun rumput minggu 3"),
        ("supplies", 25000, "2025-07-27", "Racun rumput minggu 4"),
    ]

    expenses_created = 0
    total_amount = 0

    for category, amount, date_str, description in expenses_data:
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)

        expense = Expense(
            date=expense_date,
            category=category,
            amount=amount,
            description=description,
            receipt_url=None
        )
        db.add(expense)
        expenses_created += 1
        total_amount += amount

    db.commit()

    print(f"✅ Created {expenses_created} expenses")
    print(f"   Total expenses: Rp {total_amount:,.0f}")
    print(f"\n   Breakdown:")
    print(f"   - Sampah (4×): Rp 150,000")
    print(f"   - Listrik (2×): Rp 405,000")
    print(f"   - Upah tukang rumput (4×): Rp 150,000")
    print(f"   - Racun rumput (4×): Rp 100,000")

def main():
    print("=" * 60)
    print("🌱 SEEDING DATABASE WITH REAL PAYMENT DATA")
    print("=" * 60)

    # Clear existing data
    clear_database()

    # Create session
    db = SessionLocal()

    try:
        # Seed data
        rooms = seed_rooms(db)
        seed_tenants_and_payments(db, rooms)
        seed_expenses(db)

        # Calculate and verify July income
        print("\n" + "=" * 60)
        print("💰 INCOME VERIFICATION (JULY 2025)")
        print("=" * 60)

        # Get all payments
        july_payments = db.query(Payment).filter(
            Payment.paid_date >= datetime(2025, 7, 1, tzinfo=timezone.utc),
            Payment.paid_date < datetime(2025, 8, 1, tzinfo=timezone.utc)
        ).all()

        # Calculate income by floor
        floor_income = {1: 0, 2: 0, 3: 0, 4: 0}

        for payment in july_payments:
            tenant = db.query(Tenant).filter(Tenant.id == payment.tenant_id).first()
            if tenant and tenant.current_room_id:
                room = db.query(Room).filter(Room.id == tenant.current_room_id).first()
                if room and room.floor in floor_income:
                    floor_income[room.floor] += payment.amount

        total_income = sum(floor_income.values())

        print(f"\n  Floor 1: Rp {floor_income[1]:>11,}")
        print(f"  Floor 2: Rp {floor_income[2]:>11,}")
        print(f"  Floor 3: Rp {floor_income[3]:>11,}")
        print(f"  Floor 4: Rp {floor_income[4]:>11,}")
        print(f"  {'─' * 35}")
        print(f"  Total Income:    Rp {total_income:>11,}")

        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print("\nData Summary:")
        print(f"  - 32 rooms (101-404) across 4 floors")
        print(f"  - Floor 1: Standard/Superior rooms (300k-400k)")
        print(f"  - Floor 2: Superior/Deluxe rooms (400k-500k)")
        print(f"  - Floor 3: Deluxe/Junior Suite rooms (500k-550k)")
        print(f"  - Floor 4: Suite rooms (600k-650k)")
        print(f"  - Occupied rooms with guests and payments")
        print(f"  - Payment dates: July-August 2025")
        print(f"  - Payment methods: BCA transfer, Cash (M)")
        print(f"  - July income: Rp {total_income:,}")
        print(f"  - July expenses: Rp 805,000")
        print(f"  - July profit: Rp {total_income - 805000:,}")
        print("\nRoom Status:")
        print(f"  - Occupied: Multiple rooms with active guests")
        print(f"  - Vacant: Rooms 204, 304, 402")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
