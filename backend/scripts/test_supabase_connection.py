#!/usr/bin/env python3
"""
Test Supabase connection with various formats
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Test different connection string formats
test_connections = [
    {
        "name": "Direct Connection (Port 5432)",
        "url": "postgresql+psycopg2://postgres:Sw0ZTzpYqZl6IR66@db.qcyftbttgyreoouazjfx.supabase.co:5432/postgres"
    },
    {
        "name": "Session Pooler (Port 6543)",
        "url": "postgresql+psycopg2://postgres.qcyftbttgyreoouazjfx:Sw0ZTzpYqZl6IR66@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
    },
    {
        "name": "IPv4 Pooler (Port 5432)",
        "url": "postgresql+psycopg2://postgres.qcyftbttgyreoouazjfx:Sw0ZTzpYqZl6IR66@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    },
]

print("🔍 Testing Supabase Connection Formats\n")
print("=" * 70)

for config in test_connections:
    print(f"\n📡 Testing: {config['name']}")
    print("-" * 70)

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(config['url'], pool_pre_ping=True, connect_args={"connect_timeout": 5})

        with engine.connect() as conn:
            result = conn.execute(text('SELECT version()'))
            version = result.fetchone()[0]

            print(f"✅ SUCCESS!")
            print(f"   PostgreSQL: {version.split(',')[0]}")

            # Get tables
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"))
            table_count = result.fetchone()[0]
            print(f"   Tables: {table_count}")

            print(f"\n💡 Use this connection string in your .env:")
            print(f"   DATABASE_URL={config['url']}")
            break

    except Exception as e:
        print(f"❌ FAILED: {str(e).split('(')[0]}")

print("\n" + "=" * 70)
print("\n📋 Next Steps:")
print("1. If all connections failed:")
print("   - Check if Supabase project is paused")
print("   - Restore project in Supabase dashboard")
print("   - Get fresh connection string from Settings → Database")
print("\n2. If one succeeded:")
print("   - Copy the DATABASE_URL shown above")
print("   - Update your .env file with that URL")
print("   - Run: python3 migrate_sqlite_to_supabase.py")
