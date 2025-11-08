"""
Comprehensive API tests for Rooms and Guests management
Tests CRUD operations, status updates, and availability tracking
"""

import pytest
from datetime import datetime, timedelta, date


class TestRoomTypes:
    """Test room type management"""

    def test_create_room_type(self, client, admin_token):
        """Test creating a new room type"""
        payload = {
            "name": "Premium Suite",
            "description": "Luxury premium suite with ocean view",
            "base_rate": 1500000
        }

        response = client.post(
            "/api/room-types",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Premium Suite"
        assert data["base_rate"] == 1500000
        assert "id" in data

    def test_get_room_type(self, client, user_token, room_type_data):
        """Test retrieving a room type"""
        rt = room_type_data[0]

        response = client.get(
            f"/api/room-types/{rt.id}",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == rt.id
        assert data["name"] == rt.name
        assert data["base_rate"] == rt.base_rate

    def test_list_room_types(self, client, user_token, room_type_data):
        """Test listing all room types"""
        response = client.get(
            "/api/room-types",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_update_room_type(self, client, admin_token, room_type_data):
        """Test updating a room type"""
        rt = room_type_data[0]

        payload = {
            "name": "Standard Plus",
            "description": "Upgraded standard room",
            "base_rate": 600000
        }

        response = client.put(
            f"/api/room-types/{rt.id}",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Standard Plus"
        assert data["base_rate"] == 600000

    def test_delete_room_type_as_admin(self, client, admin_token, room_type_data):
        """Test deleting a room type as admin"""
        rt = room_type_data[2]

        response = client.delete(
            f"/api/room-types/{rt.id}",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200

    def test_delete_room_type_as_user_forbidden(self, client, user_token, room_type_data):
        """Test that regular users cannot delete room types"""
        rt = room_type_data[0]

        response = client.delete(
            f"/api/room-types/{rt.id}",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        # Should be forbidden
        assert response.status_code == 403


class TestRooms:
    """Test room management"""

    def test_create_room(self, client, admin_token, room_type_data):
        """Test creating a new room"""
        payload = {
            "room_number": "101",
            "room_type_id": room_type_data[0].id,
            "status": "available"
        }

        response = client.post(
            "/api/rooms",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["room_number"] == "101"
        assert data["room_type_id"] == room_type_data[0].id
        assert data["status"] == "available"

    def test_create_duplicate_room_number(self, client, admin_token, rooms_data):
        """Test that duplicate room numbers are not allowed"""
        room = rooms_data[0]

        payload = {
            "room_number": room.room_number,
            "room_type_id": room.room_type_id,
            "status": "available"
        }

        response = client.post(
            "/api/rooms",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        # Should fail - duplicate room number
        assert response.status_code == 409

    def test_get_room(self, client, user_token, rooms_data):
        """Test retrieving a room"""
        room = rooms_data[0]

        response = client.get(
            f"/api/rooms/{room.id}",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == room.id
        assert data["room_number"] == room.room_number
        assert data["status"] == "available"

    def test_list_rooms(self, client, user_token, rooms_data):
        """Test listing all rooms"""
        response = client.get(
            "/api/rooms",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 9  # 3 room types × 3 rooms

    def test_list_rooms_by_type(self, client, user_token, room_type_data):
        """Test filtering rooms by type"""
        rt = room_type_data[0]

        response = client.get(
            f"/api/rooms",
            params={"room_type_id": rt.id},
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have 3 rooms of this type
        assert all(room["room_type_id"] == rt.id for room in data)

    def test_update_room_status(self, client, admin_token, rooms_data):
        """Test updating room status"""
        room = rooms_data[0]

        payload = {
            "room_number": room.room_number,
            "room_type_id": room.room_type_id,
            "status": "occupied"
        }

        response = client.put(
            f"/api/rooms/{room.id}",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "occupied"

    def test_update_room_status_maintenance(self, client, admin_token, rooms_data):
        """Test setting room to maintenance"""
        room = rooms_data[0]

        payload = {
            "room_number": room.room_number,
            "room_type_id": room.room_type_id,
            "status": "maintenance"
        }

        response = client.put(
            f"/api/rooms/{room.id}",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "maintenance"

    def test_delete_room(self, client, admin_token, rooms_data):
        """Test deleting a room"""
        room = rooms_data[0]

        response = client.delete(
            f"/api/rooms/{room.id}",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200


class TestGuests:
    """Test guest management"""

    def test_create_guest(self, client, user_token):
        """Test creating a new guest"""
        payload = {
            "first_name": "Michael",
            "last_name": "Johnson",
            "email": "michael@example.com",
            "phone": "083456789012",
            "address": "789 Pine Rd"
        }

        response = client.post(
            "/api/guests",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Michael"
        assert data["last_name"] == "Johnson"
        assert data["email"] == "michael@example.com"
        assert "id" in data

    def test_get_guest(self, client, user_token, guest_data):
        """Test retrieving a guest"""
        guest = guest_data[0]

        response = client.get(
            f"/api/guests/{guest.id}",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == guest.id
        assert data["first_name"] == guest.first_name
        assert data["email"] == guest.email

    def test_search_guest_by_name(self, client, user_token, guest_data):
        """Test searching guests by name"""
        guest = guest_data[0]

        response = client.get(
            f"/api/guests",
            params={"search": guest.first_name},
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(g["first_name"] == guest.first_name for g in data)

    def test_search_guest_by_email(self, client, user_token, guest_data):
        """Test searching guests by email"""
        guest = guest_data[0]

        response = client.get(
            f"/api/guests",
            params={"search": guest.email},
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(g["email"] == guest.email for g in data)

    def test_search_guest_by_phone(self, client, user_token, guest_data):
        """Test searching guests by phone"""
        guest = guest_data[0]

        response = client.get(
            f"/api/guests",
            params={"search": guest.phone},
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_guests(self, client, user_token, guest_data):
        """Test listing all guests"""
        response = client.get(
            "/api/guests",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_update_guest(self, client, user_token, guest_data):
        """Test updating a guest"""
        guest = guest_data[0]

        payload = {
            "first_name": "Jonathan",
            "last_name": "Smith",
            "email": "jonathan@example.com",
            "phone": "084567890123",
            "address": "999 New St"
        }

        response = client.put(
            f"/api/guests/{guest.id}",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jonathan"
        assert data["email"] == "jonathan@example.com"

    def test_delete_guest(self, client, admin_token, guest_data):
        """Test deleting a guest"""
        guest = guest_data[0]

        response = client.delete(
            f"/api/guests/{guest.id}",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200

    def test_delete_guest_as_user_forbidden(self, client, user_token, guest_data):
        """Test that regular users cannot delete guests"""
        guest = guest_data[0]

        response = client.delete(
            f"/api/guests/{guest.id}",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        # Should be forbidden
        assert response.status_code == 403

    def test_guest_full_name_property(self, client, user_token, guest_data):
        """Test guest full_name property"""
        guest = guest_data[0]

        response = client.get(
            f"/api/guests/{guest.id}",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        expected_full_name = f"{guest.first_name} {guest.last_name}"
        assert data.get("full_name") == expected_full_name


class TestCheckInOut:
    """Test check-in and check-out operations"""

    def test_check_in_guest(self, client, admin_token, db_session, reservation_data, rooms_data):
        """Test checking in a guest"""
        res = reservation_data[0]
        room = rooms_data[0]

        payload = {
            "room_id": room.id
        }

        response = client.post(
            f"/api/reservations/{res.id}/check-in",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "checked_in"
        assert data["room_id"] == room.id
        assert data["checked_in_by"] == admin_token["user"].id
        assert data["checked_in_at"] is not None

    def test_check_in_with_receptionist_tracking(self, client, admin_token, db_session, reservation_data, rooms_data):
        """Test that check-in tracks receptionist name"""
        res = reservation_data[0]
        room = rooms_data[0]

        payload = {
            "room_id": room.id
        }

        response = client.post(
            f"/api/reservations/{res.id}/check-in",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["checked_in_by_name"] == admin_token["user"].username

    def test_check_in_invalid_room(self, client, admin_token, reservation_data):
        """Test check-in with invalid room"""
        res = reservation_data[0]

        payload = {
            "room_id": 99999
        }

        response = client.post(
            f"/api/reservations/{res.id}/check-in",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 404

    def test_check_out_guest(self, client, admin_token, db_session, reservation_data, rooms_data):
        """Test checking out a guest"""
        from models import Payment

        res = reservation_data[0]
        room = rooms_data[0]

        # First check in
        client.post(
            f"/api/reservations/{res.id}/check-in",
            json={"room_id": room.id},
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        # Record payment
        payment = Payment(
            reservation_id=res.id,
            amount=1500000,
            payment_method="card",
            payment_type="full",
            payment_date=date.today(),
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
        assert data["status"] == "checked_out"
        assert data["checked_out_at"] is not None

    def test_check_out_nonexistent_reservation(self, client, admin_token):
        """Test checking out non-existent reservation"""
        response = client.post(
            "/api/reservations/99999/check-out",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 404
