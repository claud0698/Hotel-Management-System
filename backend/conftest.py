"""
Pytest configuration and fixtures for Hotel Management System API tests
"""

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import Generator

# Use SQLite in-memory database for tests
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create tables
    from models import Base
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a new database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)

    # Clear all tables before each test
    from models import Base
    Base.metadata.drop_all(bind=test_db_engine)
    Base.metadata.create_all(bind=test_db_engine)

    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create FastAPI test client with test database"""
    from fastapi.testclient import TestClient
    from app import create_app
    from database import get_db

    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


@pytest.fixture
def admin_token(client, db_session):
    """Create admin user and return JWT token"""
    from models import User
    from security import create_access_token
    import bcrypt

    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@hotel.test",
        full_name="Admin User",
        role="admin",
        password_hash=bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    # Create token
    token = create_access_token(
        data={"user_id": admin_user.id, "username": admin_user.username, "role": "admin"},
        expires_delta=timedelta(hours=16)
    )

    return {"token": token, "user": admin_user}


@pytest.fixture
def user_token(client, db_session):
    """Create regular user and return JWT token"""
    from models import User
    from security import create_access_token
    import bcrypt

    # Create regular user
    regular_user = User(
        username="receptionist",
        email="receptionist@hotel.test",
        full_name="John Doe",
        role="user",
        password_hash=bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
    )
    db_session.add(regular_user)
    db_session.commit()
    db_session.refresh(regular_user)

    # Create token
    token = create_access_token(
        data={"user_id": regular_user.id, "username": regular_user.username, "role": "user"},
        expires_delta=timedelta(hours=16)
    )

    return {"token": token, "user": regular_user}


@pytest.fixture
def room_type_data(db_session):
    """Create test room types"""
    from models import RoomType

    room_types = [
        RoomType(name="Standard", description="Standard room", base_rate=500000),
        RoomType(name="Deluxe", description="Deluxe room", base_rate=750000),
        RoomType(name="Suite", description="Luxury suite", base_rate=1200000),
    ]

    for rt in room_types:
        db_session.add(rt)

    db_session.commit()

    return room_types


@pytest.fixture
def rooms_data(db_session, room_type_data):
    """Create test rooms"""
    from models import Room

    rooms = []
    for room_type in room_type_data:
        for room_num in range(1, 4):  # 3 rooms per type
            room = Room(
                room_number=f"{room_type.id}{room_num:02d}",
                room_type_id=room_type.id,
                status="available"
            )
            db_session.add(room)
            rooms.append(room)

    db_session.commit()
    return rooms


@pytest.fixture
def guest_data(db_session):
    """Create test guests"""
    from models import Guest

    guests = [
        Guest(
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            phone="081234567890",
            address="123 Main St"
        ),
        Guest(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="082345678901",
            address="456 Oak Ave"
        ),
    ]

    for guest in guests:
        db_session.add(guest)

    db_session.commit()
    return guests


@pytest.fixture
def reservation_data(db_session, guest_data, room_type_data):
    """Create test reservations"""
    from models import Reservation
    from datetime import datetime, timedelta

    today = datetime.utcnow().date()

    reservations = [
        Reservation(
            confirmation_number="RES001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today + timedelta(days=1),
            check_out_date=today + timedelta(days=4),
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=1500000,
            discount_amount=0,
            total_amount=1500000,
            deposit_amount=500000,
            status="confirmed"
        ),
        Reservation(
            confirmation_number="RES002",
            guest_id=guest_data[1].id,
            room_type_id=room_type_data[1].id,
            check_in_date=today + timedelta(days=5),
            check_out_date=today + timedelta(days=7),
            adults=1,
            children=1,
            rate_per_night=750000,
            subtotal=1500000,
            discount_amount=200000,
            total_amount=1300000,
            deposit_amount=0,
            status="confirmed"
        ),
    ]

    for res in reservations:
        db_session.add(res)

    db_session.commit()
    return reservations
