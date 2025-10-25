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
    """Create 24 rooms (A1-A12, B1-B12) with different rates"""
    print("\n🏠 Creating rooms...")

    # Floor A rooms (Rp 650,000 base rate, A1 = 670k, A12 = 700k)
    floor_a_rates = {
        'A1': 670000,
        'A12': 700000
    }

    rooms_created = []

    # Floor A (A1-A12) - Floor 2 = A (Atas/Upper)
    for i in range(1, 13):
        room_number = f"A{i}"
        monthly_rate = floor_a_rates.get(room_number, 650000)  # Default 650k

        room = Room(
            room_number=room_number,
            floor=2,
            room_type="single",
            monthly_rate=monthly_rate,
            status="available",
            amenities="WiFi, AC, Bed, Table"
        )
        db.add(room)
        rooms_created.append(room)

    # Floor B (B1-B12) - Floor 1 = B (Bawah/Lower) - All Rp 700,000
    for i in range(1, 13):
        room_number = f"B{i}"
        monthly_rate = 750000 if room_number == 'B1' else 700000

        room = Room(
            room_number=room_number,
            floor=1,
            room_type="single",
            monthly_rate=monthly_rate,
            status="available",
            amenities="WiFi, AC, Bed, Table"
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
    payment_data = {
        'A1': ('BCA', 670000, '2025-07-07', 'paid'),
        'A2': ('M', 650000, '2025-07-02', 'paid'),
        'A3': ('M', 650000, '2025-07-08', 'paid'),
        'A4': ('BCA', 650000, '2025-07-02', 'paid'),
        'A5': ('BCA', 650000, '2025-07-10', 'paid'),
        'A6': ('BCA', 650000, '2025-07-18', 'paid'),
        'A7': ('BCA', 650000, '2025-07-30', 'paid'),
        'A8': ('M', 650000, '2025-08-02', 'paid'),
        'A9': ('Kabur', None, None, 'vacant'),  # Tenant ran away
        'A10': ('M', 650000, '2025-07-25', 'paid'),
        'A11': ('BCA', 650000, '2025-07-25', 'paid'),
        'A12': ('BCA', 700000, '2025-07-18', 'paid'),
        'B1': ('M', 750000, '2025-07-05', 'paid'),
        'B2': ('BCA', 700000, '2025-07-07', 'paid'),
        'B3': ('M', 700000, '2025-07-02', 'paid'),
        'B4': ('BCA', 700000, '2025-07-07', 'paid'),
        'B5': ('Kosong', None, None, 'vacant'),  # Empty
        'B6': ('M', 700000, '2025-07-07', 'paid'),
        'B7': ('M', 700000, '2025-07-30', 'paid'),
        'B8': ('BCA', 700000, '2025-07-01', 'paid'),
        'B9': ('M', 700000, '2025-08-03', 'paid'),
        'B10': ('M', 700000, '2025-07-27', 'paid'),
        'B11': ('Kosong', None, None, 'vacant'),  # Empty
        'B12': ('Anto', None, None, 'occupied'),  # Occupied but no payment yet
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
        tenant_name = f"Tenant {room_number}" if method_or_note != 'Anto' else 'Anto'
        move_in_date = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)  # Assume moved in June

        tenant = Tenant(
            name=tenant_name,
            phone=f"0812345{room_number.replace('A', '1').replace('B', '2')}",
            email=f"tenant{room_number.lower()}@example.com",
            id_number=f"31730100000{room_number.replace('A', '1').replace('B', '2')}",
            move_in_date=move_in_date,
            current_room_id=room.id,
            status='active',
            notes=method_or_note if method_or_note in ['M', 'Kabur'] else None
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

        # Calculate by floor (A = Atas, B = Bawah)
        floor_a_income = sum(p.amount for p in july_payments if 'A' in db.query(Room).join(Tenant).filter(Tenant.id == p.tenant_id).first().room_number)
        floor_b_income = sum(p.amount for p in july_payments if 'B' in db.query(Room).join(Tenant).filter(Tenant.id == p.tenant_id).first().room_number)

        # Simpler calculation - get tenant's room
        floor_a_total = 0
        floor_b_total = 0

        for payment in july_payments:
            tenant = db.query(Tenant).filter(Tenant.id == payment.tenant_id).first()
            if tenant and tenant.current_room_id:
                room = db.query(Room).filter(Room.id == tenant.current_room_id).first()
                if room:
                    if room.room_number.startswith('A'):
                        floor_a_total += payment.amount
                    else:
                        floor_b_total += payment.amount

        total_income = floor_a_total + floor_b_total

        print(f"\n  Floor A (Atas):  Rp {floor_a_total:>11,}")
        print(f"  Floor B (Bawah): Rp {floor_b_total:>11,}")
        print(f"  {'─' * 35}")
        print(f"  Total Income:    Rp {total_income:>11,}")
        print(f"\n  Expected Total:  Rp  13,570,000")
        print(f"  Difference:      Rp {total_income - 13570000:>11,}")

        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print("\nData Summary:")
        print(f"  - 24 rooms (A1-A12, B1-B12)")
        print(f"  - Floor A: Rp 650,000-700,000/month")
        print(f"  - Floor B: Rp 700,000-750,000/month")
        print(f"  - Occupied rooms with tenants and payments")
        print(f"  - Payment dates: July-August 2025")
        print(f"  - Payment methods: BCA transfer, Cash (M)")
        print(f"  - July income: Rp {total_income:,}")
        print(f"  - July expenses: Rp 805,000")
        print(f"  - July profit: Rp {total_income - 805000:,}")
        print("\nSpecial Cases:")
        print(f"  - A9: Kabur (tenant ran away)")
        print(f"  - B5, B11: Kosong (vacant)")
        print(f"  - B12: Anto (occupied, no payment yet)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
