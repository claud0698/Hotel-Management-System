#!/usr/bin/env python3
"""
Simple room seeding script for A1-A12 and B1-B12
"""

from app import SessionLocal, Base, engine
from models import Room
from datetime import datetime, timezone

def seed_rooms():
    """Seed rooms A1-A12 (Floor A) and B1-B12 (Floor B)"""
    db = SessionLocal()

    try:
        # Check if rooms already exist
        existing_count = db.query(Room).count()
        if existing_count > 0:
            print(f"Rooms already exist ({existing_count} rooms). Clearing and re-seeding...")
            db.query(Room).delete()
            db.commit()

        rooms_data = []

        # Floor A: A1 to A12
        for i in range(1, 13):
            room_number = f"A{i}"
            rooms_data.append({
                'room_number': room_number,
                'floor': 1,  # Floor A
                'room_type': 'single',
                'monthly_rate': 500000,  # 500k IDR
                'status': 'available',
                'amenities': 'WiFi, AC, Bed, Table'
            })

        # Floor B: B1 to B12
        for i in range(1, 13):
            room_number = f"B{i}"
            rooms_data.append({
                'room_number': room_number,
                'floor': 2,  # Floor B
                'room_type': 'single',
                'monthly_rate': 500000,  # 500k IDR
                'status': 'available',
                'amenities': 'WiFi, AC, Bed, Table'
            })

        # Create rooms
        created_count = 0
        for room_data in rooms_data:
            room = Room(
                room_number=room_data['room_number'],
                floor=room_data['floor'],
                room_type=room_data['room_type'],
                monthly_rate=room_data['monthly_rate'],
                status=room_data['status'],
                amenities=room_data['amenities'],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(room)
            created_count += 1

        db.commit()

        print(f"✓ Successfully created {created_count} rooms:")
        print("  - Floor A: A1 to A12")
        print("  - Floor B: B1 to B12")
        print(f"  - Monthly rate: 500,000 IDR")
        print(f"  - Type: Single room")
        print(f"  - Status: All available")

        # Display all rooms
        all_rooms = db.query(Room).order_by(Room.room_number).all()
        print(f"\nTotal rooms in database: {len(all_rooms)}")
        print("\nRoom list:")
        for room in all_rooms:
            print(f"  {room.room_number} - Floor {room.floor} - Status: {room.status} - Rate: {room.monthly_rate:,.0f} IDR")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("ROOM SEEDING - A1-A12 and B1-B12")
    print("=" * 60)
    print()

    seed_rooms()

    print()
    print("=" * 60)
    print("Seeding complete!")
    print("=" * 60)
