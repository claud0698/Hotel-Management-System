"""
Migration script to transfer data from SQLite to PostgreSQL
Run this script to migrate all data from kos.db to the PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, User, Room, Tenant, Payment, Expense, RoomHistory
from datetime import datetime

# Load environment variables
load_dotenv()

# Get database URLs
SQLITE_URL = "sqlite:///./kos.db"
POSTGRES_URL = os.getenv('DATABASE_URL')

if not POSTGRES_URL or 'sqlite' in POSTGRES_URL.lower():
    print("❌ Error: DATABASE_URL in .env must be set to PostgreSQL connection string")
    print("   Current DATABASE_URL:", POSTGRES_URL)
    sys.exit(1)

if '[YOUR-PASSWORD]' in POSTGRES_URL:
    print("❌ Error: Please replace [YOUR-PASSWORD] in .env with your actual database password")
    sys.exit(1)

print("🔄 Starting migration from SQLite to PostgreSQL...")
print(f"📍 Source: {SQLITE_URL}")
print(f"📍 Target: {POSTGRES_URL.split('@')[0].split('://')[0]}://***@{POSTGRES_URL.split('@')[1]}")

# Create engines
try:
    sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    postgres_engine = create_engine(POSTGRES_URL, pool_pre_ping=True)

    # Test PostgreSQL connection
    with postgres_engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Successfully connected to PostgreSQL database")

except Exception as e:
    print(f"❌ Database connection error: {e}")
    sys.exit(1)

# Create session makers
SQLiteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)

def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""

    # Create all tables in PostgreSQL
    print("\n📋 Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=postgres_engine)
    print("✅ Tables created successfully")

    # Create sessions
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()

    try:
        # Clear existing data in PostgreSQL (optional - comment out if you want to keep existing data)
        print("\n🗑️  Clearing existing data in PostgreSQL...")
        for table in reversed(Base.metadata.sorted_tables):
            postgres_session.execute(table.delete())
        postgres_session.commit()
        print("✅ Existing data cleared")

        # Migrate Users
        print("\n👤 Migrating users...")
        users = sqlite_session.query(User).all()
        for user in users:
            new_user = User(
                id=user.id,
                username=user.username,
                password_hash=user.password_hash,
                email=user.email,
                created_at=user.created_at
            )
            postgres_session.merge(new_user)
        postgres_session.commit()
        print(f"✅ Migrated {len(users)} users")

        # Migrate Rooms
        print("\n🏠 Migrating rooms...")
        rooms = sqlite_session.query(Room).all()
        for room in rooms:
            new_room = Room(
                id=room.id,
                room_number=room.room_number,
                floor=room.floor,
                room_type=room.room_type,
                monthly_rate=room.monthly_rate,
                status=room.status,
                amenities=room.amenities,
                created_at=room.created_at,
                updated_at=room.updated_at
            )
            postgres_session.merge(new_room)
        postgres_session.commit()
        print(f"✅ Migrated {len(rooms)} rooms")

        # Migrate Tenants
        print("\n👥 Migrating tenants...")
        tenants = sqlite_session.query(Tenant).all()
        for tenant in tenants:
            new_tenant = Tenant(
                id=tenant.id,
                name=tenant.name,
                phone=tenant.phone,
                email=tenant.email,
                id_number=tenant.id_number,
                move_in_date=tenant.move_in_date,
                move_out_date=tenant.move_out_date,
                current_room_id=tenant.current_room_id,
                status=tenant.status,
                notes=tenant.notes,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at
            )
            postgres_session.merge(new_tenant)
        postgres_session.commit()
        print(f"✅ Migrated {len(tenants)} tenants")

        # Migrate Payments
        print("\n💰 Migrating payments...")
        payments = sqlite_session.query(Payment).all()
        for payment in payments:
            new_payment = Payment(
                id=payment.id,
                tenant_id=payment.tenant_id,
                amount=payment.amount,
                due_date=payment.due_date,
                paid_date=payment.paid_date,
                status=payment.status,
                payment_method=payment.payment_method,
                receipt_number=payment.receipt_number,
                period_months=payment.period_months,
                notes=payment.notes,
                created_at=payment.created_at,
                updated_at=payment.updated_at
            )
            postgres_session.merge(new_payment)
        postgres_session.commit()
        print(f"✅ Migrated {len(payments)} payments")

        # Migrate Expenses
        print("\n💸 Migrating expenses...")
        expenses = sqlite_session.query(Expense).all()
        for expense in expenses:
            new_expense = Expense(
                id=expense.id,
                date=expense.date,
                category=expense.category,
                amount=expense.amount,
                description=expense.description,
                receipt_url=expense.receipt_url,
                created_at=expense.created_at,
                updated_at=expense.updated_at
            )
            postgres_session.merge(new_expense)
        postgres_session.commit()
        print(f"✅ Migrated {len(expenses)} expenses")

        # Migrate Room History
        print("\n📜 Migrating room history...")
        room_histories = sqlite_session.query(RoomHistory).all()
        for history in room_histories:
            new_history = RoomHistory(
                id=history.id,
                room_id=history.room_id,
                tenant_id=history.tenant_id,
                move_in_date=history.move_in_date,
                move_out_date=history.move_out_date,
                created_at=history.created_at
            )
            postgres_session.merge(new_history)
        postgres_session.commit()
        print(f"✅ Migrated {len(room_histories)} room history records")

        # Update sequences for PostgreSQL
        print("\n🔢 Updating PostgreSQL sequences...")
        tables_with_sequences = [
            ('users', 'users_id_seq'),
            ('rooms', 'rooms_id_seq'),
            ('tenants', 'tenants_id_seq'),
            ('payments', 'payments_id_seq'),
            ('expenses', 'expenses_id_seq'),
            ('room_history', 'room_history_id_seq')
        ]

        for table_name, sequence_name in tables_with_sequences:
            try:
                # Get max ID from table
                result = postgres_session.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}"))
                max_id = result.scalar()

                # Set sequence to max_id + 1
                postgres_session.execute(text(f"SELECT setval('{sequence_name}', {max_id + 1}, false)"))
                postgres_session.commit()
                print(f"✅ Updated {sequence_name} to {max_id + 1}")
            except Exception as e:
                print(f"⚠️  Warning: Could not update sequence {sequence_name}: {e}")

        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   - Users: {len(users)}")
        print(f"   - Rooms: {len(rooms)}")
        print(f"   - Tenants: {len(tenants)}")
        print(f"   - Payments: {len(payments)}")
        print(f"   - Expenses: {len(expenses)}")
        print(f"   - Room History: {len(room_histories)}")
        print("\n🎉 Your data has been successfully migrated to PostgreSQL!")
        print("💡 Your application is now using PostgreSQL database.")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        postgres_session.rollback()
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()


if __name__ == "__main__":
    try:
        # Confirm before migration
        print("\n⚠️  WARNING: This will clear existing data in the PostgreSQL database and replace it with SQLite data.")
        response = input("Do you want to continue? (yes/no): ")

        if response.lower() in ['yes', 'y']:
            migrate_data()
        else:
            print("❌ Migration cancelled by user")
    except KeyboardInterrupt:
        print("\n❌ Migration cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
