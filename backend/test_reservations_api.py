"""
Comprehensive API tests for Reservations endpoint
Tests pre-order booking, availability checking, and deposit settlement
"""

import pytest
from datetime import datetime, timedelta, date
from fastapi.testclient import TestClient


class TestReservationCRUD:
    """Test basic CRUD operations for reservations"""

    def test_create_reservation(self, client, user_token, guest_data, room_type_data):
        """Test creating a new reservation with deposit"""
        today = date.today()

        payload = {
            "guest_id": guest_data[0].id,
            "room_type_id": room_type_data[0].id,
            "check_in_date": (today + timedelta(days=7)).isoformat(),
            "check_out_date": (today + timedelta(days=10)).isoformat(),
            "adults": 2,
            "children": 0,
            "rate_per_night": 500000,
            "subtotal": 1500000,
            "discount_amount": 0,
            "total_amount": 1500000,
            "deposit_amount": 500000,
            "special_requests": "Late check-in"
        }

        response = client.post(
            "/api/reservations",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["guest_id"] == guest_data[0].id
        assert data["status"] == "confirmed"
        assert data["deposit_amount"] == 500000
        assert "confirmation_number" in data
        assert data["total_amount"] == 1500000

    def test_create_reservation_with_default_deposit(self, client, user_token, guest_data, room_type_data):
        """Test that deposit defaults to 0 if not specified"""
        today = date.today()

        payload = {
            "guest_id": guest_data[0].id,
            "room_type_id": room_type_data[0].id,
            "check_in_date": (today + timedelta(days=7)).isoformat(),
            "check_out_date": (today + timedelta(days=10)).isoformat(),
            "adults": 2,
            "children": 0,
            "rate_per_night": 500000,
            "subtotal": 1500000,
            "discount_amount": 0,
            "total_amount": 1500000,
            # No deposit_amount specified - should default to 0
            "special_requests": None
        }

        response = client.post(
            "/api/reservations",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["deposit_amount"] == 0  # Default value

    def test_get_reservation(self, client, user_token, reservation_data):
        """Test retrieving a single reservation"""
        res = reservation_data[0]

        response = client.get(
            f"/api/reservations/{res.id}",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == res.id
        assert data["confirmation_number"] == res.confirmation_number
        assert data["deposit_amount"] == 500000

    def test_get_reservation_not_found(self, client, user_token):
        """Test getting non-existent reservation"""
        response = client.get(
            "/api/reservations/99999",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 404

    def test_list_reservations(self, client, user_token, reservation_data):
        """Test listing all reservations"""
        response = client.get(
            "/api/reservations",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2


class TestAvailabilityChecking:
    """Test pre-order booking and availability checking"""

    def test_check_availability_available(self, client, user_token, room_type_data):
        """Test checking availability for future dates with available rooms"""
        today = date.today()

        response = client.get(
            "/api/reservations/availability",
            params={
                "room_type_id": room_type_data[0].id,
                "check_in_date": (today + timedelta(days=20)).isoformat(),
                "check_out_date": (today + timedelta(days=25)).isoformat(),
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_available"] is True
        assert data["available_rooms"] > 0
        assert data["total_rooms"] > 0

    def test_check_availability_no_rooms(self, client, user_token, db_session, room_type_data, reservation_data):
        """Test checking availability when all rooms are booked"""
        from models import Room

        # Get all rooms of type 0
        rooms = db_session.query(Room).filter_by(room_type_id=room_type_data[0].id).all()

        # Book all rooms for a specific period
        from models import Reservation

        today = date.today()
        check_in = today + timedelta(days=15)
        check_out = today + timedelta(days=18)

        for i, room in enumerate(rooms):
            guest = reservation_data[i % len(reservation_data)].guest
            reservation = Reservation(
                confirmation_number=f"BLOCK{i}",
                guest_id=guest.id,
                room_type_id=room_type_data[0].id,
                check_in_date=check_in,
                check_out_date=check_out,
                adults=1,
                children=0,
                rate_per_night=500000,
                subtotal=1500000,
                discount_amount=0,
                total_amount=1500000,
                deposit_amount=0,
                status="confirmed"
            )
            db_session.add(reservation)

        db_session.commit()

        # Now check availability
        response = client.get(
            "/api/reservations/availability",
            params={
                "room_type_id": room_type_data[0].id,
                "check_in_date": check_in.isoformat(),
                "check_out_date": check_out.isoformat(),
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_available"] is False
        assert data["available_rooms"] == 0

    def test_check_availability_invalid_dates(self, client, user_token, room_type_data):
        """Test availability check with invalid date range"""
        today = date.today()

        # Check-out before check-in
        response = client.get(
            "/api/reservations/availability",
            params={
                "room_type_id": room_type_data[0].id,
                "check_in_date": (today + timedelta(days=10)).isoformat(),
                "check_out_date": (today + timedelta(days=5)).isoformat(),
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 400

    def test_check_availability_past_date(self, client, user_token, room_type_data):
        """Test availability check with past check-in date"""
        today = date.today()

        response = client.get(
            "/api/reservations/availability",
            params={
                "room_type_id": room_type_data[0].id,
                "check_in_date": (today - timedelta(days=5)).isoformat(),
                "check_out_date": (today + timedelta(days=5)).isoformat(),
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 400

    def test_check_availability_invalid_room_type(self, client, user_token):
        """Test availability check with non-existent room type"""
        today = date.today()

        response = client.get(
            "/api/reservations/availability",
            params={
                "room_type_id": 99999,
                "check_in_date": (today + timedelta(days=10)).isoformat(),
                "check_out_date": (today + timedelta(days=15)).isoformat(),
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 404


class TestDepositSystem:
    """Test deposit system functionality"""

    def test_get_balance_with_deposit(self, client, user_token, reservation_data):
        """Test balance inquiry showing deposit information"""
        res = reservation_data[0]  # Has 500000 deposit

        response = client.get(
            f"/api/reservations/{res.id}/balance",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reservation_id"] == res.id
        assert data["deposit_amount"] == 500000
        assert "final_balance_after_deposit" in data
        assert data["total_amount"] == 1500000

    def test_get_balance_no_deposit(self, client, user_token, reservation_data):
        """Test balance inquiry for reservation with no deposit"""
        res = reservation_data[1]  # No deposit

        response = client.get(
            f"/api/reservations/{res.id}/balance",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["deposit_amount"] == 0
        assert data["final_balance_after_deposit"] == data["balance"]

    def test_checkout_with_full_payment(self, client, admin_token, db_session, reservation_data):
        """Test checkout when guest has paid in full - deposit should be returned"""
        from models import Payment

        res = reservation_data[0]  # 1500000 total, 500000 deposit

        # Record full payment
        payment = Payment(
            reservation_id=res.id,
            amount=1500000,
            payment_method="card",
            payment_type="full",
            payment_date=datetime.utcnow().date(),
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Now check out
        response = client.post(
            f"/api/reservations/{res.id}/check-out",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["final_balance_owed"] == 0
        assert data["deposit_settlement"]["to_refund"] == 500000
        assert "full deposit" in data["deposit_settlement"]["settlement_note"].lower()

    def test_checkout_with_partial_payment(self, client, admin_token, db_session, reservation_data):
        """Test checkout when guest has paid partially - deposit applied to balance"""
        from models import Payment

        res = reservation_data[0]  # 1500000 total, 500000 deposit

        # Record partial payment
        payment = Payment(
            reservation_id=res.id,
            amount=800000,
            payment_method="cash",
            payment_type="downpayment",
            payment_date=datetime.utcnow().date(),
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Check out - should apply deposit to balance
        response = client.post(
            f"/api/reservations/{res.id}/check-out",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        # Total: 1500000, Paid: 800000, Balance: 700000
        # Deposit: 500000, Applied to balance: 500000
        # Guest still owes: 200000
        assert data["final_balance_owed"] == 200000
        assert "still owes" in data["deposit_settlement"]["settlement_note"].lower()

    def test_checkout_with_overpayment(self, client, admin_token, db_session, reservation_data):
        """Test checkout when guest has overpaid - deposit and excess refunded"""
        from models import Payment

        res = reservation_data[0]  # 1500000 total, 500000 deposit

        # Record overpayment
        payment = Payment(
            reservation_id=res.id,
            amount=2000000,
            payment_method="transfer",
            payment_type="full",
            payment_date=datetime.utcnow().date(),
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Check out
        response = client.post(
            f"/api/reservations/{res.id}/check-out",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["final_balance_owed"] == 0
        # Should refund full deposit (500000) and overpayment (500000)
        assert data["deposit_settlement"]["to_refund"] == 500000

    def test_deposit_timestamp_at_checkout(self, client, admin_token, db_session, reservation_data):
        """Test that deposit_returned_at is set at checkout"""
        from models import Payment

        res = reservation_data[0]

        # Record payment
        payment = Payment(
            reservation_id=res.id,
            amount=1500000,
            payment_method="card",
            payment_type="full",
            payment_date=datetime.utcnow().date(),
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Check that deposit_returned_at is None before checkout
        db_session.refresh(res)
        assert res.deposit_returned_at is None

        # Check out
        response = client.post(
            f"/api/reservations/{res.id}/check-out",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200

        # Verify deposit_returned_at is now set
        db_session.refresh(res)
        assert res.deposit_returned_at is not None


class TestPreOrderBooking:
    """Test pre-order booking workflow"""

    def test_preorder_booking_future_dates(self, client, user_token, guest_data, room_type_data):
        """Test creating a pre-order booking for future dates"""
        today = date.today()

        payload = {
            "guest_id": guest_data[0].id,
            "room_type_id": room_type_data[0].id,
            "check_in_date": (today + timedelta(days=30)).isoformat(),
            "check_out_date": (today + timedelta(days=35)).isoformat(),
            "adults": 2,
            "children": 1,
            "rate_per_night": 500000,
            "subtotal": 2500000,
            "discount_amount": 100000,
            "total_amount": 2400000,
            "deposit_amount": 600000,
            "special_requests": "Early check-in requested"
        }

        response = client.post(
            "/api/reservations",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["check_in_date"] == (today + timedelta(days=30)).isoformat()

    def test_preorder_booking_prevents_double_booking(self, client, user_token, guest_data, room_type_data):
        """Test that pre-order booking prevents double-booking"""
        today = date.today()

        # Create first reservation
        payload1 = {
            "guest_id": guest_data[0].id,
            "room_type_id": room_type_data[0].id,
            "check_in_date": (today + timedelta(days=10)).isoformat(),
            "check_out_date": (today + timedelta(days=15)).isoformat(),
            "adults": 2,
            "children": 0,
            "rate_per_night": 500000,
            "subtotal": 2500000,
            "discount_amount": 0,
            "total_amount": 2500000,
            "deposit_amount": 500000,
            "special_requests": None
        }

        response1 = client.post(
            "/api/reservations",
            json=payload1,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )
        assert response1.status_code == 201

        # Try to create overlapping reservation - should fail
        payload2 = {
            "guest_id": guest_data[1].id,
            "room_type_id": room_type_data[0].id,
            "check_in_date": (today + timedelta(days=12)).isoformat(),
            "check_out_date": (today + timedelta(days=18)).isoformat(),
            "adults": 1,
            "children": 0,
            "rate_per_night": 500000,
            "subtotal": 3000000,
            "discount_amount": 0,
            "total_amount": 3000000,
            "deposit_amount": 0,
            "special_requests": None
        }

        response2 = client.post(
            "/api/reservations",
            json=payload2,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        # Should fail with conflict error
        assert response2.status_code == 409

    def test_preorder_booking_with_downpayment(self, client, admin_token, db_session, guest_data, room_type_data):
        """Test pre-order booking with downpayment (partial payment)"""
        from models import Reservation, Payment

        today = date.today()

        # Create pre-order with deposit
        res = Reservation(
            confirmation_number="PREORDER001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today + timedelta(days=30),
            check_out_date=today + timedelta(days=35),
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=2500000,
            discount_amount=0,
            total_amount=2500000,
            deposit_amount=500000,
            status="confirmed"
        )
        db_session.add(res)
        db_session.commit()

        # Record downpayment
        payment = Payment(
            reservation_id=res.id,
            amount=500000,
            payment_method="transfer",
            payment_type="downpayment",
            payment_date=datetime.utcnow().date(),
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Check balance - should show balance and deposit
        response = client.get(
            f"/api/reservations/{res.id}/balance",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_paid"] == 500000
        assert data["balance"] == 2000000
        assert data["deposit_amount"] == 500000


class TestDateValidation:
    """Test date validation for reservations"""

    def test_past_checkin_date_rejected(self, client, user_token, guest_data, room_type_data):
        """Test that past check-in dates are rejected"""
        today = date.today()

        payload = {
            "guest_id": guest_data[0].id,
            "room_type_id": room_type_data[0].id,
            "check_in_date": (today - timedelta(days=1)).isoformat(),
            "check_out_date": (today + timedelta(days=3)).isoformat(),
            "adults": 2,
            "children": 0,
            "rate_per_night": 500000,
            "subtotal": 2000000,
            "discount_amount": 0,
            "total_amount": 2000000,
            "deposit_amount": 0,
            "special_requests": None
        }

        response = client.post(
            "/api/reservations",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 400

    def test_checkout_before_checkin_rejected(self, client, user_token, guest_data, room_type_data):
        """Test that check-out date before check-in is rejected"""
        today = date.today()

        payload = {
            "guest_id": guest_data[0].id,
            "room_type_id": room_type_data[0].id,
            "check_in_date": (today + timedelta(days=5)).isoformat(),
            "check_out_date": (today + timedelta(days=3)).isoformat(),
            "adults": 2,
            "children": 0,
            "rate_per_night": 500000,
            "subtotal": 2000000,
            "discount_amount": 0,
            "total_amount": 2000000,
            "deposit_amount": 0,
            "special_requests": None
        }

        response = client.post(
            "/api/reservations",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 400


class TestAuthentication:
    """Test authentication and authorization"""

    def test_missing_token_unauthorized(self, client):
        """Test that missing token returns 401"""
        response = client.get("/api/reservations")
        assert response.status_code == 401

    def test_invalid_token_unauthorized(self, client):
        """Test that invalid token returns 401"""
        response = client.get(
            "/api/reservations",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        assert response.status_code == 401
