"""
Comprehensive API tests for Dashboard endpoints
Tests operational metrics and reporting
"""

import pytest
from datetime import datetime, timedelta, date


class TestDashboard:
    """Test dashboard and metrics endpoints"""

    def test_get_today_summary(self, client, user_token):
        """Test getting today's summary metrics"""
        response = client.get(
            "/api/dashboard/today",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have key metrics
        assert "arrivals_today" in data
        assert "departures_today" in data
        assert "occupancy_rate" in data
        assert "checked_in_count" in data

    def test_get_today_arrivals(self, client, admin_token, db_session, guest_data, room_type_data):
        """Test today's arrivals count"""
        from models import Reservation

        today = date.today()

        # Create reservation with today's check-in
        res = Reservation(
            confirmation_number="ARR001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today,
            check_out_date=today + timedelta(days=3),
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=1500000,
            discount_amount=0,
            total_amount=1500000,
            deposit_amount=0,
            status="confirmed"
        )
        db_session.add(res)
        db_session.commit()

        response = client.get(
            "/api/dashboard/today",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["arrivals_today"] >= 1

    def test_get_today_departures(self, client, admin_token, db_session, guest_data, room_type_data):
        """Test today's departures count"""
        from models import Reservation

        today = date.today()

        # Create reservation with today's check-out
        res = Reservation(
            confirmation_number="DEP001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today - timedelta(days=3),
            check_out_date=today,
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=1500000,
            discount_amount=0,
            total_amount=1500000,
            deposit_amount=0,
            status="confirmed"
        )
        db_session.add(res)
        db_session.commit()

        response = client.get(
            "/api/dashboard/today",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["departures_today"] >= 1

    def test_occupancy_rate_calculation(self, client, user_token, db_session, rooms_data, reservation_data):
        """Test occupancy rate calculation"""
        response = client.get(
            "/api/dashboard/today",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Occupancy rate should be between 0 and 100
        assert 0 <= data["occupancy_rate"] <= 100

    def test_get_metrics(self, client, user_token):
        """Test getting metrics for a period"""
        today = date.today()
        start_date = (today - timedelta(days=7)).isoformat()
        end_date = today.isoformat()

        response = client.get(
            "/api/dashboard/metrics",
            params={
                "start_date": start_date,
                "end_date": end_date
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have period metrics
        assert "period" in data
        assert "total_reservations" in data
        assert "total_revenue" in data
        assert "average_occupancy" in data

    def test_get_metrics_invalid_date_range(self, client, user_token):
        """Test metrics with invalid date range"""
        today = date.today()
        start_date = today.isoformat()
        end_date = (today - timedelta(days=7)).isoformat()

        response = client.get(
            "/api/dashboard/metrics",
            params={
                "start_date": start_date,
                "end_date": end_date
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        # Should fail - start date after end date
        assert response.status_code == 400

    def test_get_revenue_summary(self, client, user_token):
        """Test getting revenue summary"""
        response = client.get(
            "/api/dashboard/revenue",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have revenue breakdown
        assert "total_revenue" in data
        assert "collected_payments" in data
        assert "pending_balance" in data

    def test_get_summary(self, client, user_token):
        """Test getting dashboard summary"""
        response = client.get(
            "/api/dashboard/summary",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have quick stats
        assert "quick_stats" in data
        assert "recent_activity" in data


class TestOperationalMetrics:
    """Test operational metrics and reporting"""

    def test_in_house_guests(self, client, user_token, db_session, guest_data, room_type_data, rooms_data):
        """Test getting in-house guests"""
        from models import Reservation

        today = date.today()

        # Create checked-in reservation
        res = Reservation(
            confirmation_number="INHOUSE001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today - timedelta(days=1),
            check_out_date=today + timedelta(days=2),
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=1500000,
            discount_amount=0,
            total_amount=1500000,
            deposit_amount=0,
            status="checked_in",
            room_id=rooms_data[0].id
        )
        db_session.add(res)
        db_session.commit()

        response = client.get(
            "/api/dashboard/today",
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["checked_in_count"] >= 1

    def test_occupancy_changes_with_checkin(self, client, admin_token, db_session, guest_data, room_type_data, rooms_data):
        """Test that occupancy rate changes with check-in"""
        from models import Reservation

        today = date.today()

        # Get initial occupancy
        response1 = client.get(
            "/api/dashboard/today",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )
        initial_occupancy = response1.json()["occupancy_rate"]

        # Create and check in reservation
        res = Reservation(
            confirmation_number="OCC001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today,
            check_out_date=today + timedelta(days=3),
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=1500000,
            discount_amount=0,
            total_amount=1500000,
            deposit_amount=0,
            status="checked_in",
            room_id=rooms_data[0].id,
            checked_in_by=admin_token["user"].id,
            checked_in_at=datetime.utcnow()
        )
        db_session.add(res)
        db_session.commit()

        # Get new occupancy
        response2 = client.get(
            "/api/dashboard/today",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )
        new_occupancy = response2.json()["occupancy_rate"]

        # Occupancy should have increased
        assert new_occupancy >= initial_occupancy

    def test_revenue_calculation_with_payments(self, client, admin_token, db_session, guest_data, room_type_data):
        """Test that revenue is calculated from payments"""
        from models import Reservation, Payment

        today = date.today()

        # Create reservation
        res = Reservation(
            confirmation_number="REV001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today - timedelta(days=1),
            check_out_date=today + timedelta(days=2),
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=1500000,
            discount_amount=0,
            total_amount=1500000,
            deposit_amount=0,
            status="checked_in"
        )
        db_session.add(res)
        db_session.commit()

        # Record payment
        payment = Payment(
            reservation_id=res.id,
            amount=1000000,
            payment_method="card",
            payment_type="downpayment",
            payment_date=today,
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Get revenue
        response = client.get(
            "/api/dashboard/revenue",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["collected_payments"] >= 1000000

    def test_pending_balance_calculation(self, client, admin_token, db_session, guest_data, room_type_data):
        """Test pending balance calculation"""
        from models import Reservation, Payment

        today = date.today()

        # Create reservation with 1500000 total
        res = Reservation(
            confirmation_number="BAL001",
            guest_id=guest_data[0].id,
            room_type_id=room_type_data[0].id,
            check_in_date=today - timedelta(days=1),
            check_out_date=today + timedelta(days=2),
            adults=2,
            children=0,
            rate_per_night=500000,
            subtotal=1500000,
            discount_amount=0,
            total_amount=1500000,
            deposit_amount=0,
            status="checked_in"
        )
        db_session.add(res)
        db_session.commit()

        # Record partial payment
        payment = Payment(
            reservation_id=res.id,
            amount=800000,
            payment_method="cash",
            payment_type="downpayment",
            payment_date=today,
            created_by=admin_token["user"].id
        )
        db_session.add(payment)
        db_session.commit()

        # Get revenue - pending should be at least 700000
        response = client.get(
            "/api/dashboard/revenue",
            headers={"Authorization": f"Bearer {admin_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pending_balance"] >= 700000


class TestReportGeneration:
    """Test report generation endpoints"""

    def test_daily_report(self, client, user_token):
        """Test generating daily report"""
        today = date.today()

        response = client.get(
            "/api/dashboard/metrics",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat()
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert data["period"]["start"] == today.isoformat()
        assert data["period"]["end"] == today.isoformat()

    def test_weekly_report(self, client, user_token):
        """Test generating weekly report"""
        today = date.today()
        start_date = (today - timedelta(days=7)).isoformat()
        end_date = today.isoformat()

        response = client.get(
            "/api/dashboard/metrics",
            params={
                "start_date": start_date,
                "end_date": end_date
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "period" in data

    def test_monthly_report(self, client, user_token):
        """Test generating monthly report"""
        today = date.today()
        start_date = (today - timedelta(days=30)).isoformat()
        end_date = today.isoformat()

        response = client.get(
            "/api/dashboard/metrics",
            params={
                "start_date": start_date,
                "end_date": end_date
            },
            headers={"Authorization": f"Bearer {user_token['token']}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "period" in data
