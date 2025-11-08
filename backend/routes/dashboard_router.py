"""
Dashboard and analytics routes for Hotel Management System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import Optional

from models import Room, Reservation, Payment, RoomType, Guest
from security import get_current_user
from database import get_db

router = APIRouter()


@router.get("/metrics", response_model=dict)
async def get_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics for a date range"""
    # Default to current month
    now = datetime.now(timezone.utc)
    if not start_date:
        start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    else:
        start = datetime.fromisoformat(start_date)

    if not end_date:
        if now.month == 12:
            end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime.fromisoformat(end_date)

    # Room metrics
    total_rooms = db.query(Room).count()

    # Occupied rooms - count active reservations
    occupied_rooms = db.query(func.count(Room.id)).join(
        Reservation, Room.id == Reservation.room_id
    ).filter(
        Reservation.check_in_date <= now,
        Reservation.check_out_date >= now,
        Reservation.status == 'confirmed'
    ).scalar() or 0

    available_rooms = total_rooms - occupied_rooms
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    # Payment metrics
    paid_payments = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == 'completed',
        Payment.paid_at >= start,
        Payment.paid_at < end
    ).scalar() or 0.0

    pending_payments = db.query(Payment).filter(
        Payment.status == 'pending'
    ).count()

    # Overdue payments
    overdue_payments = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == 'pending',
        Payment.due_date < now
    ).scalar() or 0.0

    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "available_rooms": available_rooms,
        "occupancy_rate": round(occupancy_rate, 2),
        "total_income": float(paid_payments),
        "pending_payments": pending_payments,
        "overdue_amount": float(overdue_payments),
        "start_date": start.isoformat(),
        "end_date": end.isoformat()
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
