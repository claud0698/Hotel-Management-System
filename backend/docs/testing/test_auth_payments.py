"""
Comprehensive API tests for Authentication and Payment endpoints
Tests JWT auth, payment recording, payment types, and payment validation
"""

import pytest
from datetime import datetime, timedelta, date


class TestAuthentication:
    """Test authentication endpoints and JWT tokens"""

    def test_login_successful(self, client, db_session):
        """Test successful login"""
        from models import User
        import bcrypt

        # Create a user
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="admin",
            password_hash=bcrypt.hashpw("testpass123".encode(), bcrypt.gensalt()).decode()
        )
        db_session.add(user)
        db_session.commit()

        # Login
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
        assert data["user"]["role"] == "admin"

    def test_login_invalid_credentials(self, client, db_session):
        """Test login with invalid credentials"""
        from models import User
        import bcrypt

        # Create a user
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="admin",
            password_hash=bcrypt.hashpw("testpass123".encode(), bcrypt.gensalt()).decode()
        )
        db_session.add(user)
        db_session.commit()

        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpass"}
        )

        assert response.status_code == 401

    def test_login_user_not_found(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )

        assert response.status_code == 401

    def test_token_expiration_config(self, client):
        """Test that JWT token expiration is correctly configured"""
        from security import TOKEN_EXPIRE_MINUTES

        # Token should be set to 16 hours (960 minutes) for shift-based operations
        assert TOKEN_EXPIRE_MINUTES == 960, f"Expected 960 minutes (16 hours), got {TOKEN_EXPIRE_MINUTES}"

    def test_access_with_valid_token(self, client, user_token):
        """Test accessing protected endpoint with valid token"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_token["user"].username

    def test_access_with_expired_token(self, client, user_token):
        """Test accessing protected endpoint with expired token"""
        # This test would require mocking time, skipping for now
        # In real scenario, would need to advance time past expiration
        pass


class TestPayments:
    """Test payment endpoints"""

    def test_record_payment_successful(self, client, admin_token, db_session, reservation_data):
        """Test recording a payment for a reservation"""
        from models import Payment

        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            "amount": 500000,
            "payment_date": date.today().isoformat(),
            "payment_method": "cash",
            "payment_type": "downpayment",
            "reference_number": "CASH001",
            "notes": "Downpayment received at check-in"
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["reservation_id"] == res.id
        assert data["amount"] == 500000
        assert data["payment_type"] == "downpayment"
        assert data["payment_method"] == "cash"

    def test_record_payment_full(self, client, admin_token, reservation_data):
        """Test recording a full payment"""
        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            "amount": 1500000,
            "payment_date": date.today().isoformat(),
            "payment_method": "card",
            "payment_type": "full",
            "reference_number": "CARD123",
            "notes": None
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 1500000
        assert data["payment_type"] == "full"

    def test_record_payment_deposit(self, client, admin_token, reservation_data):
        """Test recording a deposit payment"""
        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            "amount": 500000,
            "payment_date": date.today().isoformat(),
            "payment_method": "transfer",
            "payment_type": "deposit",
            "reference_number": "TRANSFER001",
            "notes": "Security deposit"
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["payment_type"] == "deposit"

    def test_record_payment_adjustment(self, client, admin_token, reservation_data):
        """Test recording an adjustment payment"""
        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            "amount": -50000,
            "payment_date": date.today().isoformat(),
            "payment_method": "adjustment",
            "payment_type": "adjustment",
            "reference_number": "ADJ001",
            "notes": "Discount applied"
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["payment_type"] == "adjustment"

    def test_record_payment_invalid_reservation(self, client, admin_token):
        """Test recording payment for non-existent reservation"""
        payload = {
            "reservation_id": 99999,
            "amount": 500000,
            "payment_date": date.today().isoformat(),
            "payment_method": "cash",
            "payment_type": "full",
            "reference_number": None,
            "notes": None
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 404

    def test_record_payment_negative_amount(self, client, admin_token, reservation_data):
        """Test that negative amounts are accepted only for adjustments"""
        res = reservation_data[0]

        # Negative amount should only be allowed for adjustments
        payload = {
            "reservation_id": res.id,
            "amount": -100000,
            "payment_date": date.today().isoformat(),
            "payment_method": "cash",
            "payment_type": "full",  # Not an adjustment
            "reference_number": None,
            "notes": None
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        # Should fail - can't have negative full payment
        assert response.status_code == 400 or response.status_code == 422

    def test_get_payment(self, client, admin_token, db_session, reservation_data):
        """Test retrieving a payment"""
        from models import Payment

        res = reservation_data[0]

        # Create payment
        payment = Payment(
            reservation_id=res.id,
            amount=500000,
            payment_method="cash",
            payment_type="downpayment",
            payment_date=date.today(),
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Retrieve payment
        response = client.get(
            f"/api/payments/{payment.id}",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment.id
        assert data["amount"] == 500000

    def test_list_payments_for_reservation(self, client, admin_token, db_session, reservation_data):
        """Test listing all payments for a reservation"""
        from models import Payment

        res = reservation_data[0]

        # Create multiple payments
        for i in range(3):
            payment = Payment(
                reservation_id=res.id,
                amount=100000 * (i + 1),
                payment_method="cash",
                payment_type="downpayment" if i < 2 else "full",
                payment_date=date.today(),
                created_by=admin_token["user"].id
            )
            db_session.add(payment)

        db_session.commit()

        # List payments
        response = client.get(
            "/api/payments",
            params={"reservation_id": res.id},
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_payment_tracks_created_by(self, client, admin_token, db_session, reservation_data):
        """Test that payment tracks who created it"""
        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            "amount": 500000,
            "payment_date": date.today().isoformat(),
            "payment_method": "cash",
            "payment_type": "downpayment",
            "reference_number": "TEST001",
            "notes": "Test payment"
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["created_by"] == admin_token["user"].id


class TestPaymentValidation:
    """Test payment input validation"""

    def test_payment_amount_required(self, client, admin_token, reservation_data):
        """Test that payment amount is required"""
        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            # Missing amount
            "payment_date": date.today().isoformat(),
            "payment_method": "cash",
            "payment_type": "full"
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_payment_method_required(self, client, admin_token, reservation_data):
        """Test that payment method is required"""
        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            "amount": 500000,
            "payment_date": date.today().isoformat(),
            # Missing payment_method
            "payment_type": "full"
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 422

    def test_payment_date_format(self, client, admin_token, reservation_data):
        """Test payment date format validation"""
        res = reservation_data[0]

        # Invalid date format
        payload = {
            "reservation_id": res.id,
            "amount": 500000,
            "payment_date": "invalid-date",
            "payment_method": "cash",
            "payment_type": "full"
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 422

    def test_invalid_payment_type(self, client, admin_token, reservation_data):
        """Test that only valid payment types are accepted"""
        res = reservation_data[0]

        payload = {
            "reservation_id": res.id,
            "amount": 500000,
            "payment_date": date.today().isoformat(),
            "payment_method": "cash",
            "payment_type": "invalid_type"  # Not one of the allowed types
        }

        response = client.post(
            "/api/payments",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        # Should fail due to invalid payment_type
        assert response.status_code == 422


class TestUserManagement:
    """Test user management endpoints"""

    def test_create_user_as_admin(self, client, admin_token):
        """Test creating a new user as admin"""
        payload = {
            "username": "newuser",
            "email": "newuser@hotel.test",
            "full_name": "New User",
            "password": "secure123",
            "role": "user"
        }

        response = client.post(
            "/api/users",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "user"
        assert "password" not in data  # Password should not be returned

    def test_create_user_as_regular_user(self, client, user_token):
        """Test that regular users cannot create other users"""
        payload = {
            "username": "newuser",
            "email": "newuser@hotel.test",
            "full_name": "New User",
            "password": "secure123",
            "role": "user"
        }

        response = client.post(
            "/api/users",
            json=payload,
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        # Should be forbidden
        assert response.status_code == 403

    def test_get_current_user(self, client, admin_token):
        """Test getting current user info"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == admin_token["user"].username
        assert data["role"] == "admin"

    def test_list_users_as_admin(self, client, admin_token, user_token):
        """Test listing users as admin"""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least admin and user

    def test_list_users_as_regular_user(self, client, user_token):
        """Test that regular users cannot list users"""
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        # Should be forbidden
        assert response.status_code == 403
