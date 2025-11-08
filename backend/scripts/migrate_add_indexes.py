"""
Migration Script: Add Performance Indexes
Adds all the new indexes for performance optimization
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# List of indexes to create
indexes = [
    # Room indexes
    "CREATE INDEX IF NOT EXISTS idx_room_status ON rooms(status);",

    # Tenant indexes
    "CREATE INDEX IF NOT EXISTS idx_tenant_status ON tenants(status);",
    "CREATE INDEX IF NOT EXISTS idx_tenant_room ON tenants(current_room_id);",

    # Payment indexes
    "CREATE INDEX IF NOT EXISTS idx_payment_status ON payments(status);",
    "CREATE INDEX IF NOT EXISTS idx_payment_due_date ON payments(due_date);",
    "CREATE INDEX IF NOT EXISTS idx_payment_paid_date ON payments(paid_date);",
    "CREATE INDEX IF NOT EXISTS idx_payment_tenant ON payments(tenant_id);",

    # Expense indexes
    "CREATE INDEX IF NOT EXISTS idx_expense_date ON expenses(date);",
    "CREATE INDEX IF NOT EXISTS idx_expense_category ON expenses(category);",

    # Room history indexes
    "CREATE INDEX IF NOT EXISTS idx_room_history_room ON room_history(room_id);",
    "CREATE INDEX IF NOT EXISTS idx_room_history_tenant ON room_history(tenant_id);",
    "CREATE INDEX IF NOT EXISTS idx_room_history_move_in ON room_history(move_in_date);",
    "CREATE INDEX IF NOT EXISTS idx_room_history_move_out ON room_history(move_out_date);",
]

print("🚀 Adding Performance Indexes to Database\n")
print(f"Database: PostgreSQL (Supabase)\n")

with engine.connect() as conn:
    for idx_sql in indexes:
        try:
            # Extract index name for display
            idx_name = idx_sql.split("idx_")[1].split(" ON")[0]
            table_name = idx_sql.split(" ON ")[1].split("(")[0].strip()

            print(f"Creating idx_{idx_name} on {table_name}...", end=" ")
            conn.execute(text(idx_sql))
            conn.commit()
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")

print("\n✅ Migration Complete!")
print("\nVerifying indexes...")

# Verify indexes were created
from sqlalchemy import inspect
inspector = inspect(engine)

tables = ['rooms', 'tenants', 'payments', 'expenses', 'room_history']
total_indexes = 0

for table in tables:
    indexes = inspector.get_indexes(table)
    count = len(indexes)
    total_indexes += count
    print(f"  {table}: {count} indexes")

print(f"\n📊 Total indexes created: {total_indexes}")
print("🎉 Database is now optimized for performance!")
