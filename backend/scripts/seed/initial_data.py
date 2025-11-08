#!/usr/bin/env python3
"""
Seed initial data into database
- Room types
- Booking channels
- Default settings
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

load_dotenv()

def seed_initial_data():
    """Seed initial data into database"""
    try:
        print("\n" + "=" * 70)
        print("🏨 HOTEL MANAGEMENT SYSTEM - SEED INITIAL DATA")
        print("=" * 70 + "\n")

        # Import models and database
        print("1. Importing database components...")
        try:
            from models import (
                RoomType, BookingChannel, Setting,
                Base
            )
            from database import SessionLocal, engine
            print("   ✓ Imports successful")
        except ImportError as e:
            print(f"   ❌ Failed to import: {str(e)}")
            return 1

        # Create session
        print("\n2. Creating database session...")
        db = SessionLocal()

        try:
            # Seed Room Types
            print("\n3. Seeding room types...")
            room_types_data = [
                {
                    'name': 'Standard',
                    'code': 'STD',
                    'description': 'Standard room with basic amenities',
                    'base_capacity_adults': 2,
                    'base_capacity_children': 1,
                    'bed_config': 'Double bed or Twin beds',
                    'default_rate': 500000,
                    'amenities': 'WiFi, AC, TV, Bathroom, Shower',
                    'max_occupancy': 3,
                    'is_active': True
                },
                {
                    'name': 'Deluxe',
                    'code': 'DLX',
                    'description': 'Deluxe room with ocean view',
                    'base_capacity_adults': 2,
                    'base_capacity_children': 2,
                    'bed_config': 'King bed or Queen bed',
                    'default_rate': 750000,
                    'amenities': 'WiFi, AC, Smart TV, Spacious bathroom, Bath tub, Ocean view',
                    'max_occupancy': 4,
                    'is_active': True
                },
                {
                    'name': 'Suite',
                    'code': 'SUI',
                    'description': 'Luxury suite with living area',
                    'base_capacity_adults': 4,
                    'base_capacity_children': 2,
                    'bed_config': 'King bed + sofa bed',
                    'default_rate': 1200000,
                    'amenities': 'WiFi, AC, Smart TV, Living area, Kitchenette, Jacuzzi tub, Premium toiletries',
                    'max_occupancy': 6,
                    'is_active': True
                },
                {
                    'name': 'Penthouse',
                    'code': 'PNT',
                    'description': 'Premium penthouse with terrace',
                    'base_capacity_adults': 4,
                    'base_capacity_children': 2,
                    'bed_config': 'King bed + sofa bed',
                    'default_rate': 2000000,
                    'amenities': 'All suite amenities + Terrace, Concierge service, Breakfast included',
                    'max_occupancy': 6,
                    'is_active': True
                }
            ]

            created_room_types = 0
            for rt_data in room_types_data:
                existing = db.query(RoomType).filter(RoomType.code == rt_data['code']).first()
                if not existing:
                    room_type = RoomType(**rt_data)
                    db.add(room_type)
                    created_room_types += 1
                    print(f"   ✓ Created: {rt_data['name']} ({rt_data['code']})")
                else:
                    print(f"   • Skipped: {rt_data['name']} (already exists)")

            db.commit()
            print(f"\n   Total room types created: {created_room_types}")

            # Seed Booking Channels
            print("\n4. Seeding booking channels...")
            channels_data = [
                {
                    'name': 'Direct Booking',
                    'code': 'direct',
                    'description': 'Walk-in, phone, email, website bookings',
                    'channel_type': 'direct',
                    'is_enabled': True,
                    'commission_percentage': 0
                },
                {
                    'name': 'Tiket.com',
                    'code': 'tiket',
                    'description': 'Tiket.com OTA integration',
                    'channel_type': 'ota',
                    'is_enabled': True,
                    'commission_percentage': 15
                },
                {
                    'name': 'Traveloka',
                    'code': 'traveloka',
                    'description': 'Traveloka OTA integration',
                    'channel_type': 'ota',
                    'is_enabled': True,
                    'commission_percentage': 18
                },
                {
                    'name': 'Booking.com',
                    'code': 'booking',
                    'description': 'Booking.com OTA integration',
                    'channel_type': 'ota',
                    'is_enabled': True,
                    'commission_percentage': 20
                },
                {
                    'name': 'Other',
                    'code': 'other',
                    'description': 'Other booking sources',
                    'channel_type': 'direct',
                    'is_enabled': True,
                    'commission_percentage': 0
                }
            ]

            created_channels = 0
            for ch_data in channels_data:
                existing = db.query(BookingChannel).filter(BookingChannel.code == ch_data['code']).first()
                if not existing:
                    channel = BookingChannel(**ch_data)
                    db.add(channel)
                    created_channels += 1
                    print(f"   ✓ Created: {ch_data['name']}")
                else:
                    print(f"   • Skipped: {ch_data['name']} (already exists)")

            db.commit()
            print(f"\n   Total channels created: {created_channels}")

            # Seed Settings
            print("\n5. Seeding default settings...")
            settings_data = [
                ('hotel_name', 'My Hotel', 'string', True, 'Hotel name', 'Hotel Information'),
                ('hotel_address', 'Hotel Address', 'string', True, 'Hotel physical address', 'Hotel Information'),
                ('hotel_phone', '+62-xxx-xxx-xxx', 'string', True, 'Hotel contact phone', 'Hotel Information'),
                ('check_in_time', '14:00', 'string', True, 'Standard check-in time', 'Booking Configuration'),
                ('check_out_time', '12:00', 'string', True, 'Standard check-out time', 'Booking Configuration'),
                ('timezone', 'Asia/Jakarta', 'string', True, 'Hotel timezone', 'Localization'),
                ('currency', 'IDR', 'string', True, 'Hotel currency code', 'Localization'),
                ('default_language', 'id', 'string', True, 'Default language (en/id)', 'Localization'),
            ]

            created_settings = 0
            for setting_key, setting_value, setting_type, is_editable, description, category in settings_data:
                existing = db.query(Setting).filter(Setting.setting_key == setting_key).first()
                if not existing:
                    setting = Setting(
                        setting_key=setting_key,
                        setting_value=setting_value,
                        setting_type=setting_type,
                        is_editable=is_editable,
                        description=description,
                        category=category
                    )
                    db.add(setting)
                    created_settings += 1
                    print(f"   ✓ Created: {setting_key}")
                else:
                    print(f"   • Skipped: {setting_key} (already exists)")

            db.commit()
            print(f"\n   Total settings created: {created_settings}")

        except Exception as e:
            db.rollback()
            print(f"\n   ❌ Error seeding data: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            db.close()

        # Summary
        print("\n" + "=" * 70)
        print("✓ Initial data seeded successfully!")
        print("=" * 70 + "\n")

        print("Seeded:")
        print(f"  - Room types: {created_room_types}")
        print(f"  - Booking channels: {created_channels}")
        print(f"  - Settings: {created_settings}")
        print()

        print("Next steps:")
        print("1. Create admin user: python backend/init_admin.py")
        print("2. Start backend: cd backend && uvicorn app:app --reload")
        print("3. Access API: http://localhost:8000/api/docs")
        print()

        return 0

    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(seed_initial_data())
