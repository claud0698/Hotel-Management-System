#!/usr/bin/env python3
"""
Comprehensive Database Setup Script
Combines: Database initialization, data seeding, and testing
Run once to fully set up the Hotel Management System database
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


class DatabaseSetup:
    """Main database setup orchestrator"""

    def __init__(self):
        self.db = None
        self.engine = None
        self.stats = {
            'tables_created': 0,
            'indexes_created': 0,
            'room_types_seeded': 0,
            'channels_seeded': 0,
            'settings_seeded': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }

    def print_header(self, title):
        """Print section header"""
        print("\n" + "=" * 70)
        print(f"🏨 {title}")
        print("=" * 70 + "\n")

    def print_step(self, step_num, title):
        """Print step header"""
        print(f"\n{step_num}. {title}")
        print("-" * 70)

    def check_environment(self):
        """Verify environment configuration"""
        self.print_step("1", "Checking Environment Configuration")

        required_vars = ['DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing = [var for var in required_vars if not os.getenv(var)]

        if missing:
            print(f"❌ Missing environment variables: {', '.join(missing)}")
            print("   Make sure .env file exists in backend/ directory")
            return False

        database_url = os.getenv('DATABASE_URL')
        masked_url = database_url.split('@')[0] + '...@' + database_url.split('@')[1] if '@' in database_url else database_url
        print(f"✓ Database URL: {masked_url}")
        print(f"✓ All required environment variables present")
        return True

    def import_models(self):
        """Import SQLAlchemy models"""
        self.print_step("2", "Importing Models")

        try:
            from models import (
                Base, User, RoomType, Room, RoomImage, RoomTypeImage,
                Guest, Reservation, Payment, PaymentAttachment,
                Setting, Discount, BookingChannel
            )
            from database import SessionLocal, engine

            self.Base = Base
            self.SessionLocal = SessionLocal
            self.engine = engine
            self.models = {
                'User': User,
                'RoomType': RoomType,
                'Room': Room,
                'RoomImage': RoomImage,
                'RoomTypeImage': RoomTypeImage,
                'Guest': Guest,
                'Reservation': Reservation,
                'Payment': Payment,
                'PaymentAttachment': PaymentAttachment,
                'Setting': Setting,
                'Discount': Discount,
                'BookingChannel': BookingChannel
            }

            print(f"✓ Successfully imported 12 models")
            return True
        except ImportError as e:
            print(f"❌ Failed to import models: {str(e)}")
            return False

    def test_connection(self):
        """Test database connection"""
        self.print_step("3", "Testing Database Connection")

        try:
            from sqlalchemy import text

            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✓ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False

    def create_tables(self):
        """Create all database tables"""
        self.print_step("4", "Creating Database Tables")

        try:
            from sqlalchemy import inspect

            # Check existing tables
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())

            print(f"Existing tables: {len(existing_tables)}")

            # Create all tables from models
            self.Base.metadata.create_all(bind=self.engine)

            # Verify creation
            inspector = inspect(self.engine)
            new_tables = set(inspector.get_table_names())
            created_tables = new_tables - existing_tables

            self.stats['tables_created'] = len(new_tables)

            print(f"\n✓ Tables created/verified: {len(new_tables)}/12")
            for table in sorted(new_tables):
                if table in created_tables:
                    print(f"  ✓ {table} (NEW)")
                else:
                    print(f"  • {table} (existing)")

            # Count indexes
            total_indexes = 0
            for table_name in inspector.get_table_names():
                indexes = inspector.get_indexes(table_name)
                total_indexes += len(indexes)

            self.stats['indexes_created'] = total_indexes
            print(f"\n✓ Indexes created: {total_indexes}")

            return len(new_tables) == 12
        except Exception as e:
            print(f"❌ Failed to create tables: {str(e)}")
            return False

    def seed_room_types(self):
        """Seed room types"""
        print("\n  Seeding Room Types...")

        try:
            from models import RoomType

            db = self.SessionLocal()
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

            for rt_data in room_types_data:
                existing = db.query(RoomType).filter(RoomType.code == rt_data['code']).first()
                if not existing:
                    room_type = RoomType(**rt_data)
                    db.add(room_type)
                    self.stats['room_types_seeded'] += 1
                    print(f"    ✓ {rt_data['name']} ({rt_data['code']})")

            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False

    def seed_booking_channels(self):
        """Seed booking channels"""
        print("\n  Seeding Booking Channels...")

        try:
            from models import BookingChannel

            db = self.SessionLocal()
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

            for ch_data in channels_data:
                existing = db.query(BookingChannel).filter(BookingChannel.code == ch_data['code']).first()
                if not existing:
                    channel = BookingChannel(**ch_data)
                    db.add(channel)
                    self.stats['channels_seeded'] += 1
                    print(f"    ✓ {ch_data['name']}")

            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False

    def seed_settings(self):
        """Seed default settings"""
        print("\n  Seeding Default Settings...")

        try:
            from models import Setting

            db = self.SessionLocal()
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
                    self.stats['settings_seeded'] += 1
                    print(f"    ✓ {setting_key}")

            db.commit()
            db.close()
            return True
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return False

    def seed_initial_data(self):
        """Seed all initial data"""
        self.print_step("5", "Seeding Initial Data")

        success = True
        success = self.seed_room_types() and success
        success = self.seed_booking_channels() and success
        success = self.seed_settings() and success

        if success:
            print(f"\n✓ Initial data seeded successfully")
            print(f"  - Room types: {self.stats['room_types_seeded']}")
            print(f"  - Booking channels: {self.stats['channels_seeded']}")
            print(f"  - Settings: {self.stats['settings_seeded']}")

        return success

    def test_database(self):
        """Run database tests"""
        self.print_step("6", "Running Database Tests")

        try:
            from sqlalchemy import inspect

            db = self.SessionLocal()
            inspector = inspect(self.engine)

            # Test 1: Check all tables exist
            print("\n  Test 1: Verify all tables exist")
            expected_tables = {
                'users', 'room_types', 'rooms', 'room_images', 'room_type_images',
                'guests', 'reservations', 'payments', 'payment_attachments',
                'settings', 'discounts', 'booking_channels'
            }
            existing_tables = set(inspector.get_table_names())
            if expected_tables.issubset(existing_tables):
                print("    ✓ All 12 tables exist")
                self.stats['tests_passed'] += 1
            else:
                missing = expected_tables - existing_tables
                print(f"    ❌ Missing tables: {missing}")
                self.stats['tests_failed'] += 1

            # Test 2: Check room types were seeded
            print("\n  Test 2: Verify room types seeded")
            from models import RoomType

            room_types = db.query(RoomType).all()
            if len(room_types) == 4:
                print(f"    ✓ 4 room types found")
                for rt in room_types:
                    print(f"      - {rt.name} ({rt.code}): IDR {rt.default_rate:,}")
                self.stats['tests_passed'] += 1
            else:
                print(f"    ❌ Expected 4 room types, found {len(room_types)}")
                self.stats['tests_failed'] += 1

            # Test 3: Check booking channels were seeded
            print("\n  Test 3: Verify booking channels seeded")
            from models import BookingChannel

            channels = db.query(BookingChannel).all()
            if len(channels) == 5:
                print(f"    ✓ 5 booking channels found")
                for ch in channels:
                    print(f"      - {ch.name} ({ch.code})")
                self.stats['tests_passed'] += 1
            else:
                print(f"    ❌ Expected 5 channels, found {len(channels)}")
                self.stats['tests_failed'] += 1

            # Test 4: Check settings were seeded
            print("\n  Test 4: Verify settings seeded")
            from models import Setting

            settings = db.query(Setting).all()
            if len(settings) >= 8:
                print(f"    ✓ {len(settings)} settings found")
                self.stats['tests_passed'] += 1
            else:
                print(f"    ❌ Expected 8+ settings, found {len(settings)}")
                self.stats['tests_failed'] += 1

            # Test 5: Verify indexes
            print("\n  Test 5: Verify database indexes")
            total_indexes = 0
            for table_name in inspector.get_table_names():
                indexes = inspector.get_indexes(table_name)
                total_indexes += len(indexes)

            if total_indexes >= 40:
                print(f"    ✓ {total_indexes} indexes found (expected: 42+)")
                self.stats['tests_passed'] += 1
            else:
                print(f"    ⚠ Only {total_indexes} indexes found (expected: 42+)")

            db.close()
            return self.stats['tests_failed'] == 0

        except Exception as e:
            print(f"    ❌ Tests failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def print_summary(self):
        """Print final summary"""
        self.print_header("SETUP SUMMARY")

        print("Database Infrastructure Created:")
        print(f"  ✓ Tables created: {self.stats['tables_created']}/12")
        print(f"  ✓ Indexes created: {self.stats['indexes_created']}")

        print("\nInitial Data Seeded:")
        print(f"  ✓ Room types: {self.stats['room_types_seeded']}")
        print(f"  ✓ Booking channels: {self.stats['channels_seeded']}")
        print(f"  ✓ Settings: {self.stats['settings_seeded']}")

        print("\nTests Passed:")
        print(f"  ✓ Tests passed: {self.stats['tests_passed']}")
        if self.stats['tests_failed'] > 0:
            print(f"  ❌ Tests failed: {self.stats['tests_failed']}")

        total_seeded = (self.stats['room_types_seeded'] +
                       self.stats['channels_seeded'] +
                       self.stats['settings_seeded'])

        print(f"\nTotal Records Seeded: {total_seeded}")

        print("\n" + "=" * 70)
        if self.stats['tests_failed'] == 0 and self.stats['tables_created'] == 12:
            print("✓ Database setup completed successfully!")
            print("=" * 70)
            print("\nNext Steps:")
            print("1. Create admin user: python backend/init_admin.py")
            print("2. Start backend: cd backend && uvicorn app:app --reload")
            print("3. Access API: http://localhost:8000/api/docs")
            return 0
        else:
            print("⚠ Database setup completed with warnings")
            print("=" * 70)
            return 1

    def run(self):
        """Execute full setup"""
        self.print_header("HOTEL MANAGEMENT SYSTEM - COMPREHENSIVE DATABASE SETUP")

        steps = [
            ("Check Environment", self.check_environment),
            ("Import Models", self.import_models),
            ("Test Connection", self.test_connection),
            ("Create Tables", self.create_tables),
            ("Seed Initial Data", self.seed_initial_data),
            ("Run Tests", self.test_database),
        ]

        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n❌ {step_name} failed. Stopping setup.")
                    return 1
            except Exception as e:
                print(f"\n❌ {step_name} failed with error: {str(e)}")
                import traceback
                traceback.print_exc()
                return 1

        return self.print_summary()


def main():
    """Main entry point"""
    setup = DatabaseSetup()
    return setup.run()


if __name__ == "__main__":
    sys.exit(main())
