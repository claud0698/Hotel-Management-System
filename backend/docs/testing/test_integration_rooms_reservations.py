"""
Integration tests for Rooms & Reservations combined workflows.

These tests verify that rooms and reservations systems work together correctly,
including availability checking, check-in/out with room status changes, and
deposit settlement calculations.
"""

import pytest
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app import app
from models import (
    RoomType, Room, Guest, Reservation, Payment, User
)
from schemas import (
    ReservationCreate, CheckInRequest, CheckOutRequest, PaymentCreate
)


@pytest.fixture
def admin_token(db: Session, client: TestClient):
    """Get admin authentication token."""
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def receptionist_token(db: Session, client: TestClient):
    """Get receptionist authentication token."""
    # Create receptionist user
    receptionist = User(
        username="receptionist",
        password_hash="hashed_password",
        role="receptionist"
    )
    db.add(receptionist)
    db.commit()

    response = client.post(
        "/api/auth/login",
        json={"username": "receptionist", "password": "password123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def setup_rooms(db: Session):
    """Create test room types and rooms."""
    # Create room types
    deluxe = RoomType(
        name="Deluxe Double",
        description="Spacious double room",
        capacity=2,
        base_rate=500000,
        amenities=["WiFi", "AC", "TV"]
    )
    standard = RoomType(
        name="Standard Single",
        description="Compact single room",
        capacity=1,
        base_rate=300000,
        amenities=["WiFi", "AC"]
    )
    db.add_all([deluxe, standard])
    db.commit()

    # Create rooms
    rooms = []
    for i in range(1, 6):
        room = Room(
            room_number=f"10{i}",
            room_type_id=deluxe.id,
            floor=1,
            status="available"
        )
        rooms.append(room)

    for i in range(6, 9):
        room = Room(
            room_number=f"10{i}",
            room_type_id=standard.id,
            floor=1,
            status="available"
        )
        rooms.append(room)

    db.add_all(rooms)
    db.commit()

    return {"deluxe": deluxe, "standard": standard, "rooms": rooms}


@pytest.fixture
def setup_guests(db: Session):
    """Create test guests."""
    guests = [
        Guest(
            name="John Doe",
            email="john@example.com",
            phone_number="+62812345678",
            country="Indonesia",
            id_type="passport",
            id_number="A123456789"
        ),
        Guest(
            name="Jane Smith",
            email="jane@example.com",
            phone_number="+62812345679",
            country="Indonesia",
            id_type="passport",
            id_number="B987654321"
        ),
        Guest(
            name="Robert Chen",
            email="robert@example.com",
            phone_number="+62812345680",
            country="Singapore",
            id_type="passport",
            id_number="C555555555"
        )
    ]
    db.add_all(guests)
    db.commit()

    return guests


# ============================================================================
# CORE WORKFLOW TESTS
# ============================================================================

class TestStandardBookingWorkflow:
    """Test complete booking to checkout workflow."""

    def test_full_workflow_same_day_booking_and_checkout(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """
        Test: Guest books, checks in, stays, and checks out same day.
        Workflow: Availability → Create → Check-in → Check-out
        """
        guest = setup_guests[0]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Step 1: Check availability
        avail_response = client.get(
            "/api/reservations/availability",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "room_type_id": room_type.id,
                "check_in": str(today),
                "check_out": str(tomorrow)
            }
        )
        assert avail_response.status_code == 200
        data = avail_response.json()
        assert data["is_available"]
        assert data["available_rooms"] == 5

        # Step 2: Create reservation
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000,
                "notes": "Test booking"
            }
        )
        assert res_response.status_code == 201
        reservation = res_response.json()
        res_id = reservation["id"]
        assert reservation["status"] == "confirmed"
        assert reservation["room_id"] is None

        # Step 3: Record deposit payment
        payment_response = client.post(
            "/api/payments",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "reservation_id": res_id,
                "amount": 250000,
                "payment_type": "cash",
                "notes": "Deposit"
            }
        )
        assert payment_response.status_code == 201

        # Step 4: Check-in
        room = setup_rooms["rooms"][0]
        checkin_response = client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={
                "room_id": room.id,
                "require_payment": False
            }
        )
        assert checkin_response.status_code == 200
        checked_in = checkin_response.json()
        assert checked_in["status"] == "checked_in"
        assert checked_in["room_id"] == room.id
        assert checked_in["checked_in_by_name"] == "receptionist"

        # Verify room is now occupied
        room_response = client.get(
            f"/api/rooms/{room.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert room_response.json()["status"] == "occupied"

        # Step 5: Check-out (full payment)
        checkout_response = client.post(
            f"/api/reservations/{res_id}/check-out",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={
                "amount_paid": 250000,
                "payment_type": "cash",
                "notes": "Final payment"
            }
        )
        assert checkout_response.status_code == 200
        checked_out = checkout_response.json()
        assert checked_out["status"] == "checked_out"
        assert checked_out["total_paid"] == 500000
        assert checked_out["to_refund"] == 0
        assert checked_out["settlement_note"] == "Full payment received. No deposit refund."

        # Verify room is available again
        room_response = client.get(
            f"/api/rooms/{room.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert room_response.json()["status"] == "available"

    def test_multi_night_stay_workflow(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """Test: 3-night stay booking."""
        guest = setup_guests[1]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        checkout_date = today + timedelta(days=3)

        # Create reservation
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(checkout_date),
                "total_amount": 1500000,
                "deposit_amount": 750000
            }
        )
        assert res_response.status_code == 201
        res_id = res_response.json()["id"]

        # Check-in
        room = setup_rooms["rooms"][1]
        checkin_response = client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )
        assert checkin_response.status_code == 200

        # Check-out
        checkout_response = client.post(
            f"/api/reservations/{res_id}/check-out",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={
                "amount_paid": 750000,
                "payment_type": "card"
            }
        )
        assert checkout_response.status_code == 200
        checked_out = checkout_response.json()

        # Guest owes remaining 750000 (1500000 - 750000)
        assert checked_out["balance_owed"] == 750000
        assert checked_out["to_refund"] == 0


# ============================================================================
# AVAILABILITY & DOUBLE-BOOKING TESTS
# ============================================================================

class TestDoubleBookingPrevention:
    """Test that double-booking is prevented."""

    def test_overlapping_reservations_prevented(
        self, client: TestClient, db: Session, admin_token: str,
        setup_rooms: dict, setup_guests: list
    ):
        """
        Test: Two guests cannot book same room type for overlapping dates.
        """
        guest1 = setup_guests[0]
        guest2 = setup_guests[1]
        room_type = setup_rooms["deluxe"]
        today = date.today()

        # Guest 1 books Nov 12-15
        res1_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest1.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(today + timedelta(days=3)),
                "total_amount": 1000000,
                "deposit_amount": 500000
            }
        )
        assert res1_response.status_code == 201

        # Guest 2 tries to book Nov 13-14 (overlaps with Guest 1)
        res2_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest2.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today + timedelta(days=1)),
                "check_out_date": str(today + timedelta(days=2)),
                "total_amount": 600000,
                "deposit_amount": 300000
            }
        )
        assert res2_response.status_code == 409
        assert "No rooms available" in res2_response.json()["detail"]

        # Guest 2 can book Nov 15-17 (no overlap)
        res2_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest2.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today + timedelta(days=3)),
                "check_out_date": str(today + timedelta(days=5)),
                "total_amount": 600000,
                "deposit_amount": 300000
            }
        )
        assert res2_response.status_code == 201

    def test_exact_boundary_dates_allowed(
        self, client: TestClient, db: Session, admin_token: str,
        setup_rooms: dict, setup_guests: list
    ):
        """
        Test: If Guest A checks out on Nov 15, Guest B can check in on Nov 15.
        """
        guest1 = setup_guests[0]
        guest2 = setup_guests[1]
        room_type = setup_rooms["deluxe"]
        today = date.today()

        # Guest 1: Nov 10-15
        res1_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
        json={
                "guest_id": guest1.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(today + timedelta(days=5)),
                "total_amount": 1000000,
                "deposit_amount": 500000
            }
        )
        assert res1_response.status_code == 201

        # Guest 2: Nov 15-17 (same checkout date as Guest 1's checkout)
        res2_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest2.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today + timedelta(days=5)),
                "check_out_date": str(today + timedelta(days=7)),
                "total_amount": 600000,
                "deposit_amount": 300000
            }
        )
        assert res2_response.status_code == 201


# ============================================================================
# DEPOSIT SETTLEMENT TESTS
# ============================================================================

class TestDepositSettlement:
    """Test deposit settlement calculations."""

    def test_partial_payment_with_deposit_refund(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """
        Test: Guest pays deposit but only partial balance, gets partial refund.

        Setup:
        - Total: 1000000
        - Deposit: 400000
        - Guest pays: 400000 (deposit) + 500000 (balance) = 900000
        - Owes: 100000

        Settlement:
        - Balance owed: 100000
        - Deposit >= balance, so refund: 400000 - 100000 = 300000
        """
        guest = setup_guests[0]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Create reservation
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 1000000,
                "deposit_amount": 400000
            }
        )
        res_id = res_response.json()["id"]

        # Record payments
        # Payment 1: Deposit
        client.post(
            "/api/payments",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "reservation_id": res_id,
                "amount": 400000,
                "payment_type": "cash"
            }
        )

        # Check-in
        room = setup_rooms["rooms"][0]
        client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )

        # Payment 2: Partial balance
        client.post(
            "/api/payments",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "reservation_id": res_id,
                "amount": 500000,
                "payment_type": "card"
            }
        )

        # Check-out
        checkout_response = client.post(
            f"/api/reservations/{res_id}/check-out",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={
                "amount_paid": 0,
                "payment_type": "none"
            }
        )

        checked_out = checkout_response.json()
        assert checked_out["total_paid"] == 900000
        assert checked_out["balance_owed"] == 100000
        assert checked_out["to_refund"] == 300000
        assert "100000 IDR" in checked_out["settlement_note"]
        assert "300000 IDR" in checked_out["settlement_note"]

    def test_overpayment_full_refund(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """
        Test: Guest overpays, should receive full refund.

        Setup:
        - Total: 400000
        - Deposit: 300000
        - Guest pays: 450000 (overpaid by 50000)

        Settlement:
        - Balance: -50000 (overpaid)
        - Refund: 300000 (deposit) + 50000 (overpayment) = 350000
        """
        guest = setup_guests[1]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Create reservation
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 400000,
                "deposit_amount": 300000
            }
        )
        res_id = res_response.json()["id"]

        # Guest pays more than total
        client.post(
            "/api/payments",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "reservation_id": res_id,
                "amount": 450000,
                "payment_type": "card"
            }
        )

        # Check-in
        room = setup_rooms["rooms"][1]
        client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )

        # Check-out
        checkout_response = client.post(
            f"/api/reservations/{res_id}/check-out",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={
                "amount_paid": 0,
                "payment_type": "none"
            }
        )

        checked_out = checkout_response.json()
        assert checked_out["total_paid"] == 450000
        assert checked_out["balance_owed"] == 0
        assert checked_out["to_refund"] == 350000
        assert "overpaid" in checked_out["settlement_note"].lower()


# ============================================================================
# STATE TRANSITION TESTS
# ============================================================================

class TestStateTransitions:
    """Test valid and invalid state transitions."""

    def test_cannot_checkin_twice(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """Test: Cannot check-in reservation that's already checked in."""
        guest = setup_guests[0]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Create and check-in
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000
            }
        )
        res_id = res_response.json()["id"]

        room = setup_rooms["rooms"][0]
        client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )

        # Try to check-in again
        second_checkin = client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )
        assert second_checkin.status_code == 409
        assert "already been checked in" in second_checkin.json()["detail"]

    def test_cannot_checkout_before_checkin(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """Test: Cannot check-out reservation that hasn't been checked in."""
        guest = setup_guests[1]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Create reservation (don't check-in)
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000
            }
        )
        res_id = res_response.json()["id"]

        # Try to check-out without checking in
        checkout_response = client.post(
            f"/api/reservations/{res_id}/check-out",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={
                "amount_paid": 0,
                "payment_type": "none"
            }
        )
        assert checkout_response.status_code == 422
        assert "checked in" in checkout_response.json()["detail"].lower()

    def test_cannot_cancel_after_checkin(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """Test: Cannot cancel reservation after check-in."""
        guest = setup_guests[2]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Create and check-in
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000
            }
        )
        res_id = res_response.json()["id"]

        room = setup_rooms["rooms"][2]
        client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )

        # Try to cancel
        cancel_response = client.delete(
            f"/api/reservations/{res_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert cancel_response.status_code == 409


# ============================================================================
# ROOM ASSIGNMENT TESTS
# ============================================================================

class TestRoomAssignment:
    """Test room assignment during check-in."""

    def test_cannot_checkin_wrong_room_type(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """Test: Cannot assign room of wrong type during check-in."""
        guest = setup_guests[0]
        deluxe_type = setup_rooms["deluxe"]
        standard_type = setup_rooms["standard"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Book Deluxe room
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": deluxe_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000
            }
        )
        res_id = res_response.json()["id"]

        # Try to assign Standard room
        standard_room = setup_rooms["rooms"][5]  # First standard room
        checkin_response = client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": standard_room.id, "require_payment": False}
        )
        assert checkin_response.status_code == 422
        assert "room type" in checkin_response.json()["detail"].lower()

    def test_cannot_checkin_occupied_room(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """Test: Cannot assign room that's already occupied."""
        guest1 = setup_guests[0]
        guest2 = setup_guests[1]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Guest 1 books and checks in
        res1_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest1.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000
            }
        )
        res1_id = res1_response.json()["id"]

        room = setup_rooms["rooms"][0]
        client.post(
            f"/api/reservations/{res1_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )

        # Guest 2 books different date but tries to use same room
        res2_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest2.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000
            }
        )
        res2_id = res2_response.json()["id"]

        # Try to check-in with occupied room
        checkin_response = client.post(
            f"/api/reservations/{res2_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )
        assert checkin_response.status_code == 409
        assert "not available" in checkin_response.json()["detail"].lower()


# ============================================================================
# RECEPTIONIST AUDIT TRAIL TESTS
# ============================================================================

class TestReceptionistAuditTrail:
    """Test that receptionist actions are tracked."""

    def test_checkin_records_receptionist(
        self, client: TestClient, db: Session, admin_token: str,
        receptionist_token: str, setup_rooms: dict, setup_guests: list
    ):
        """Test: Check-in records which receptionist performed the action."""
        guest = setup_guests[0]
        room_type = setup_rooms["deluxe"]
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Create and check-in
        res_response = client.post(
            "/api/reservations",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "guest_id": guest.id,
                "room_type_id": room_type.id,
                "check_in_date": str(today),
                "check_out_date": str(tomorrow),
                "total_amount": 500000,
                "deposit_amount": 250000
            }
        )
        res_id = res_response.json()["id"]

        room = setup_rooms["rooms"][0]
        checkin_response = client.post(
            f"/api/reservations/{res_id}/check-in",
            headers={"Authorization": f"Bearer {receptionist_token}"},
            json={"room_id": room.id, "require_payment": False}
        )

        # Verify receptionist is recorded
        checked_in = checkin_response.json()
        assert checked_in["checked_in_by"] is not None
        assert checked_in["checked_in_by_name"] == "receptionist"
        assert checked_in["checked_in_at"] is not None

        # Verify in GET request
        get_response = client.get(
            f"/api/reservations/{res_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        res_data = get_response.json()
        assert res_data["checked_in_by_name"] == "receptionist"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
