#!/usr/bin/env python3
"""
Wait for Supabase DNS to propagate and connection to be ready
This script will retry every 30 seconds until connection succeeds
"""

import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
MAX_RETRIES = 20  # 20 retries * 30 seconds = 10 minutes max
RETRY_INTERVAL = 30  # seconds

print("🕐 Waiting for Supabase to be ready...")
print(f"   This can take 5-10 minutes for DNS propagation")
print(f"   Will retry every {RETRY_INTERVAL} seconds (max {MAX_RETRIES} attempts)")
print("=" * 70)

for attempt in range(1, MAX_RETRIES + 1):
    print(f"\n🔄 Attempt {attempt}/{MAX_RETRIES}...")

    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={'connect_timeout': 10})

        with engine.connect() as conn:
            result = conn.execute(text('SELECT version()'))
            version = result.fetchone()[0]

            print(f"\n✅ SUCCESS! Supabase is ready!")
            print(f"   PostgreSQL: {version.split(',')[0]}")

            # Check tables
            result = conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema='public'
            """))
            table_count = result.fetchone()[0]
            print(f"   Tables: {table_count}")

            print(f"\n🎉 You can now run the migration!")
            print(f"   Command: python3 migrate_sqlite_to_supabase.py")
            exit(0)

    except Exception as e:
        error_msg = str(e)

        if 'could not translate host name' in error_msg:
            print(f"   ⏳ DNS not ready yet...")
        elif 'Tenant or user not found' in error_msg:
            print(f"   ⏳ Project still initializing...")
        else:
            print(f"   ❌ Error: {error_msg.split(chr(10))[0]}")

        if attempt < MAX_RETRIES:
            print(f"   💤 Waiting {RETRY_INTERVAL} seconds before retry...")
            time.sleep(RETRY_INTERVAL)
        else:
            print(f"\n❌ Failed after {MAX_RETRIES} attempts")
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check your Supabase dashboard - is project active?")
            print(f"   2. Verify connection string in Settings → Database")
            print(f"   3. Try getting a fresh connection string")
            exit(1)

print("\n❌ Maximum retries reached. Please check your Supabase project.")
