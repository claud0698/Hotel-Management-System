"""
Seed script for July 2025 data
Updates the database with actual July 2025 payment records
"""

import sys
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, Room, Tenant, Payment, Expense

# Database setup
DATABASE_URL = "sqlite:///kos.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def clear_database(db):
    """Clear existing data"""
    print("Clearing existing data...")
    db.query(Payment).delete()
    db.query(Tenant).delete()
    db.query(Room).delete()
    db.query(Expense).delete()
    db.commit()
    print("Database cleared.")

def seed_rooms(db):
    """Create 24 rooms (A1-A12, B1-B12)"""
    print("\nCreating rooms...")

    rooms_data = []

    # Floor A (Atas/Upper) - Floor 2
    for i in range(1, 13):
        room_number = f"A{i}"
        if i == 12:
            monthly_rate = 700000  # A12 is more expensive
        else:
            monthly_rate = 650000 if i >= 2 else 670000  # A1 is 670k

        rooms_data.append({
            'room_number': room_number,
            'floor': 2,
            'room_type': 'single',
            'monthly_rate': monthly_rate,
            'status': 'occupied' if i != 9 else 'available',  # A9 is vacant (Kabur)
            'amenities': 'WiFi, AC, Bed'
        })

    # Floor B (Bawah/Lower) - Floor 1
    for i in range(1, 13):
        room_number = f"B{i}"
        monthly_rate = 750000 if i == 1 else 700000  # B1 is 750k

        status = 'occupied'
        if i in [5, 11]:  # B5 and B11 are vacant (Kosong)
            status = 'available'

        rooms_data.append({
            'room_number': room_number,
            'floor': 1,
            'room_type': 'single',
            'monthly_rate': monthly_rate,
            'status': status,
            'amenities': 'WiFi, AC, Bed'
        })

    for room_data in rooms_data:
        room = Room(**room_data)
        db.add(room)

    db.commit()
    print(f"Created {len(rooms_data)} rooms")
    return {r.room_number: r for r in db.query(Room).all()}

def seed_tenants_and_payments(db, rooms):
    """Create tenants and their July 2025 payments"""
    print("\nCreating tenants and payments...")

    # Payment data from the table
    tenant_data = [
        # Room, Tenant Name, Amount, Payment Method, Payment Date, Notes
        ('A1', 'Tenant A1', 670000, 'transfer', '2025-07-07', 'BCA Transfer'),
        ('A2', 'Tenant A2', 650000, 'cash', '2025-07-02', 'Cash'),
        ('A3', 'Tenant A3', 650000, 'cash', '2025-07-08', 'Cash'),
        ('A4', 'Tenant A4', 650000, 'transfer', '2025-07-02', 'BCA Transfer'),
        ('A5', 'Tenant A5', 650000, 'transfer', '2025-07-10', 'BCA Transfer'),
        ('A6', 'Tenant A6', 650000, 'transfer', '2025-07-18', 'BCA Transfer'),
        ('A7', 'Tenant A7', 650000, 'transfer', '2025-07-30', 'BCA Transfer'),
        ('A8', 'Tenant A8', 650000, 'cash', '2025-08-02', 'Cash - August payment'),
        # A9 is Kabur (left) - no tenant
        ('A10', 'Tenant A10', 650000, 'cash', '2025-07-25', 'Cash'),
        ('A11', 'Tenant A11', 650000, 'transfer', '2025-07-25', 'BCA Transfer'),
        ('A12', 'Tenant A12', 700000, 'transfer', '2025-07-18', 'BCA Transfer'),
        ('B1', 'Tenant B1', 750000, 'cash', '2025-07-05', 'Cash'),
        ('B2', 'Tenant B2', 700000, 'transfer', '2025-07-07', 'BCA Transfer'),
        ('B3', 'Tenant B3', 700000, 'cash', '2025-07-02', 'Cash'),
        ('B4', 'Tenant B4', 700000, 'transfer', '2025-07-07', 'BCA Transfer'),
        # B5 is Kosong (vacant) - no tenant
        ('B6', 'Tenant B6', 700000, 'cash', '2025-07-07', 'Cash'),
        ('B7', 'Tenant B7', 700000, 'cash', '2025-07-30', 'Cash'),
        ('B8', 'Tenant B8', 700000, 'transfer', '2025-07-01', 'BCA Transfer'),
        ('B9', 'Tenant B9', 700000, 'cash', '2025-08-03', 'Cash - August payment'),
        ('B10', 'Tenant B10', 700000, 'cash', '2025-07-27', 'Cash'),
        # B11 is Kosong (vacant) - no tenant
        ('B12', 'Anto', 0, None, None, 'Not yet paid'),  # Anto hasn't paid
    ]

    payment_count = 0
    tenant_count = 0

    for room_number, tenant_name, amount, payment_method, payment_date, notes in tenant_data:
        room = rooms[room_number]

        # Create tenant
        tenant = Tenant(
            name=tenant_name,
            phone=f'+62812345{tenant_count:05d}',
            email=f'{tenant_name.lower().replace(" ", "")}@example.com',
            id_number=f'1234567890{tenant_count:06d}',
            move_in_date=datetime(2025, 1, 1),  # Assume moved in January
            current_room_id=room.id,
            status='active',
            notes=notes if 'Kabur' in tenant_name or 'Kosong' in tenant_name else None
        )
        db.add(tenant)
        db.flush()  # Get tenant ID
        tenant_count += 1

        # Create payment if amount > 0
        if amount > 0 and payment_date:
            payment_datetime = datetime.strptime(payment_date, '%Y-%m-%d')

            payment = Payment(
                tenant_id=tenant.id,
                amount=amount,
                due_date=datetime(2025, 7, 1),  # July 2025 payment
                paid_date=payment_datetime,
                status='paid',
                payment_method=payment_method,
                notes=notes,
                period_months=1
            )
            db.add(payment)
            payment_count += 1
        elif room_number == 'B12':
            # Anto has a pending payment
            payment = Payment(
                tenant_id=tenant.id,
                amount=room.monthly_rate,
                due_date=datetime(2025, 7, 1),
                paid_date=None,
                status='pending',
                payment_method=None,
                notes='Anto - not yet paid',
                period_months=1
            )
            db.add(payment)
            payment_count += 1

    db.commit()
    print(f"Created {tenant_count} tenants and {payment_count} payment records")

def seed_expenses(db):
    """Create July 2025 expenses (using same pattern as before)"""
    print("\nCreating expenses...")

    expenses_data = [
        # (category, amount, date, description)
        ('utilities', 37500, '2025-07-05', 'Sampah minggu 1'),
        ('utilities', 37500, '2025-07-12', 'Sampah minggu 2'),
        ('utilities', 37500, '2025-07-19', 'Sampah minggu 3'),
        ('utilities', 37500, '2025-07-26', 'Sampah minggu 4'),
        ('utilities', 202500, '2025-07-10', 'Listrik bulan Juli (bagian 1)'),
        ('utilities', 202500, '2025-07-25', 'Listrik bulan Juli (bagian 2)'),
        ('maintenance', 37500, '2025-07-08', 'Upah tukang rumput minggu 1'),
        ('maintenance', 37500, '2025-07-15', 'Upah tukang rumput minggu 2'),
        ('maintenance', 37500, '2025-07-22', 'Upah tukang rumput minggu 3'),
        ('maintenance', 37500, '2025-07-27', 'Upah tukang rumput minggu 4'),
        ('supplies', 25000, '2025-07-06', 'Racun rumput minggu 1'),
        ('supplies', 25000, '2025-07-13', 'Racun rumput minggu 2'),
        ('supplies', 25000, '2025-07-20', 'Racun rumput minggu 3'),
        ('supplies', 25000, '2025-07-27', 'Racun rumput minggu 4'),
    ]

    for category, amount, date_str, description in expenses_data:
        expense = Expense(
            date=datetime.strptime(date_str, '%Y-%m-%d'),
            category=category,
            amount=amount,
            description=description
        )
        db.add(expense)

    db.commit()
    print(f"Created {len(expenses_data)} expense records")

    # Calculate totals
    total = sum(amount for _, amount, _, _ in expenses_data)
    print(f"Total expenses: Rp {total:,}")

def main():
    """Main seeding function"""
    print("=" * 60)
    print("Seeding database with July 2025 data...")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Clear existing data
        clear_database(db)

        # Seed data
        rooms = seed_rooms(db)
        seed_tenants_and_payments(db, rooms)
        seed_expenses(db)

        # Verify data
        print("\n" + "=" * 60)
        print("Verification:")
        print("=" * 60)

        total_rooms = db.query(Room).count()
        occupied_rooms = db.query(Room).filter(Room.status == 'occupied').count()
        total_tenants = db.query(Tenant).count()
        total_payments = db.query(Payment).filter(Payment.status == 'paid').count()
        total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == 'paid').scalar() or 0
        total_expenses = db.query(func.sum(Expense.amount)).scalar() or 0

        print(f"Total rooms: {total_rooms}")
        print(f"Occupied rooms: {occupied_rooms}")
        print(f"Total tenants: {total_tenants}")
        print(f"Total paid payments (July): {total_payments}")
        print(f"Total revenue (July): Rp {total_revenue:,.0f}")
        print(f"Total expenses (July): Rp {total_expenses:,.0f}")
        print(f"Net profit (July): Rp {(total_revenue - total_expenses):,.0f}")

        print("\n" + "=" * 60)
        print("✅ Database seeded successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    main()
