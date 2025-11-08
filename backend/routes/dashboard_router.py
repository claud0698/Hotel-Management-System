"""
Dashboard and analytics routes for Hotel Management System

Provides operational metrics and reporting:
- GET /api/dashboard/today - Today's summary (arrivals, departures, occupancy)
- GET /api/dashboard/metrics - Period metrics (start_date, end_date, defaults to current month)
- GET /api/dashboard/summary - Summary with upcoming check-ins and distributions
- GET /api/dashboard/revenue - Revenue breakdown by day and room type
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timezone, timedelta, date
from typing import Optional

from models import Room, Reservation, Payment, RoomType, Guest
from security import get_current_user
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/today", response_model=dict)
async def get_today_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get today's operational summary.

    **Returns**:
    - arrivals_today: Guests checking in today
    - departures_today: Guests checking out today
    - in_house: Currently checked-in guests
    - available_rooms: Rooms available right now
    - total_rooms: Total room count
    - occupancy_rate: Current occupancy percentage
    - rooms_by_status: Breakdown by status (available, occupied, out_of_order)
    """
    now = datetime.now(timezone.utc)
    today = now.date()

    # Count today's arrivals (confirmed reservations with check_in = today)
    arrivals_today = db.query(Reservation).filter(
        Reservation.check_in_date == today,
        Reservation.status == 'confirmed'
    ).count()

    # Count today's departures (checked-in reservations with check_out = today)
    departures_today = db.query(Reservation).filter(
        Reservation.check_out_date == today,
        Reservation.status == 'checked_in'
    ).count()

    # Count in-house guests (currently checked-in)
    in_house = db.query(Reservation).filter(
        Reservation.status == 'checked_in'
    ).count()

    # Room status breakdown
    total_rooms = db.query(Room).count()
    available_rooms = db.query(Room).filter(Room.status == 'available').count()
    occupied_rooms = db.query(Room).filter(Room.status == 'occupied').count()
    out_of_order_rooms = db.query(Room).filter(Room.status == 'out_of_order').count()

    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0.0

    return {
        "date": today.isoformat(),
        "arrivals_today": arrivals_today,
        "departures_today": departures_today,
        "in_house": in_house,
        "available_rooms": available_rooms,
        "total_rooms": total_rooms,
        "occupancy_rate": round(occupancy_rate, 2),
        "rooms_by_status": {
            "available": available_rooms,
            "occupied": occupied_rooms,
            "out_of_order": out_of_order_rooms
        }
    }


@router.get("/metrics", response_model=dict)
async def get_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD), defaults to 1st of current month"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD), defaults to 1st of next month"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard metrics for a date range.

    **Query Parameters**:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - Defaults to current calendar month if not specified

    **Returns**:
    - Occupancy metrics (rooms, occupancy rate)
    - Payment metrics (total income, pending, overdue)
    - Reservation count in period
    """
    # Default to current month
    now = datetime.now(timezone.utc)
    if not start_date:
        start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    else:
        start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)

    if not end_date:
        if now.month == 12:
            end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)

    # Room metrics (current state, not historical)
    total_rooms = db.query(Room).count()
    occupied_rooms = db.query(Room).filter(Room.status == 'occupied').count()
    available_rooms = total_rooms - occupied_rooms
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    # Payment metrics (for the period)
    total_revenue = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.payment_date >= start.date(),
        Payment.payment_date < end.date()
    ).scalar() or 0.0

    pending_payments = db.query(Payment).filter(
        Payment.payment_date >= start.date(),
        Payment.payment_date < end.date()
    ).count()

    # Reservation count in period
    reservations_count = db.query(Reservation).filter(
        Reservation.created_at >= start,
        Reservation.created_at < end
    ).count()

    return {
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "available_rooms": available_rooms,
        "occupancy_rate": round(occupancy_rate, 2),
        "total_revenue": float(total_revenue),
        "payment_count": pending_payments,
        "reservations_count": reservations_count
    }


@router.get("/summary", response_model=dict)
async def get_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary data for dashboard"""
    now = datetime.now(timezone.utc)

    # Recent reservations
    recent_reservations = db.query(Reservation).order_by(
        Reservation.created_at.desc()
    ).limit(5).all()

    # Recent payments
    recent_payments = db.query(Payment).order_by(
        Payment.created_at.desc()
    ).limit(5).all()

    # Upcoming check-ins (next 7 days)
    week_ahead = now + timedelta(days=7)
    upcoming_checkins = db.query(Reservation).filter(
        Reservation.check_in_date >= now,
        Reservation.check_in_date <= week_ahead,
        Reservation.status == 'confirmed'
    ).count()

    # Room type distribution
    room_distribution = db.query(
        RoomType.name,
        func.count(Room.id).label('count')
    ).join(Room, RoomType.id == Room.room_type_id).group_by(RoomType.id).all()

    return {
        "recent_reservations": [r.to_dict() for r in recent_reservations],
        "recent_payments": [p.to_dict() for p in recent_payments],
        "upcoming_checkins": upcoming_checkins,
        "room_distribution": [
            {"room_type": rt, "count": count} for rt, count in room_distribution
        ]
    }


@router.get("/revenue", response_model=dict)
async def get_revenue(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get revenue breakdown for the last N days"""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    # Daily revenue
    daily_revenue = db.query(
        func.date(Payment.paid_at).label('date'),
        func.coalesce(func.sum(Payment.amount), 0).label('amount')
    ).filter(
        Payment.status == 'completed',
        Payment.paid_at >= start_date,
        Payment.paid_at <= now
    ).group_by(func.date(Payment.paid_at)).all()

    # Revenue by room type
    revenue_by_type = db.query(
        RoomType.name,
        func.coalesce(func.sum(Payment.amount), 0).label('amount')
    ).join(
        Reservation, Reservation.room_type_id == RoomType.id
    ).join(
        Payment, Payment.reservation_id == Reservation.id
    ).filter(
        Payment.status == 'completed',
        Payment.paid_at >= start_date,
        Payment.paid_at <= now
    ).group_by(RoomType.id).all()

    total_revenue = sum([amount for _, amount in daily_revenue])

    return {
        "total_revenue": float(total_revenue),
        "daily_revenue": [
            {"date": str(date), "amount": float(amount)}
            for date, amount in daily_revenue
        ],
        "revenue_by_type": [
            {"room_type": room_type, "amount": float(amount)}
            for room_type, amount in revenue_by_type
        ],
        "period_days": days
    }
