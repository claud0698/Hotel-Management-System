"""
Utility functions for Kos Management Dashboard
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from models import Payment, Room, Tenant, RoomHistory


def calculate_occupancy_rate(db: Session) -> float:
    """Calculate overall occupancy rate (current/real-time)"""
    total_rooms = db.query(Room).count()
    if total_rooms == 0:
        return 0.0

    occupied_rooms = db.query(Room).filter(Room.status == 'occupied').count()
    return round((occupied_rooms / total_rooms) * 100, 2)


def calculate_historical_occupancy_rate(db: Session, start_date: datetime, end_date: datetime) -> float:
    """
    Calculate historical occupancy rate for a specific date range.

    A room is considered occupied during the period if there's a room_history record where:
    - move_in_date <= end_date
    - AND (move_out_date is NULL OR move_out_date >= start_date)

    This captures all rooms that were occupied at any point during the period.
    """
    total_rooms = db.query(Room).count()
    if total_rooms == 0:
        return 0.0

    # Count distinct rooms that were occupied during this period
    occupied_rooms = db.query(RoomHistory.room_id).distinct().filter(
        and_(
            RoomHistory.move_in_date <= end_date,
            or_(
                RoomHistory.move_out_date.is_(None),
                RoomHistory.move_out_date >= start_date
            )
        )
    ).count()

    return round((occupied_rooms / total_rooms) * 100, 2)


def get_room_occupancy_details(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get detailed room occupancy statistics.

    If start_date and end_date are provided, calculates historical occupancy.
    Otherwise, returns current/real-time occupancy.
    """
    total = db.query(Room).count()

    # If date range provided, use historical calculation
    if start_date and end_date:
        # Count distinct rooms occupied during the period
        occupied = db.query(RoomHistory.room_id).distinct().filter(
            and_(
                RoomHistory.move_in_date <= end_date,
                or_(
                    RoomHistory.move_out_date.is_(None),
                    RoomHistory.move_out_date >= start_date
                )
            )
        ).count()

        # For historical data, available = total - occupied
        available = total - occupied
        occupancy_rate = calculate_historical_occupancy_rate(db, start_date, end_date)

        return {
            'total_rooms': total,
            'available_rooms': available,
            'occupied_rooms': occupied,
            'maintenance_rooms': 0,  # Historical data doesn't track maintenance
            'reserved_rooms': 0,  # Historical data doesn't track reserved
            'occupancy_rate': occupancy_rate
        }
    else:
        # Current/real-time occupancy
        available = db.query(Room).filter(Room.status == 'available').count()
        occupied = db.query(Room).filter(Room.status == 'occupied').count()
        maintenance = db.query(Room).filter(Room.status == 'maintenance').count()
        reserved = db.query(Room).filter(Room.status == 'reserved').count()

        return {
            'total_rooms': total,
            'available_rooms': available,
            'occupied_rooms': occupied,
            'maintenance_rooms': maintenance,
            'reserved_rooms': reserved,
            'occupancy_rate': calculate_occupancy_rate(db)
        }


def get_payment_statistics(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get payment statistics using optimized database aggregations.
    This avoids loading all payment objects into memory.
    """
    # Base query with date filters
    base_query = db.query(Payment)
    if start_date:
        base_query = base_query.filter(Payment.due_date >= start_date)
    if end_date:
        base_query = base_query.filter(Payment.due_date <= end_date)

    # Use database aggregations instead of loading all records into memory
    # Get counts by status
    paid_stats = db.query(
        func.count(Payment.id).label('count'),
        func.coalesce(func.sum(Payment.amount), 0).label('total')
    ).filter(Payment.status == 'paid')

    if start_date:
        paid_stats = paid_stats.filter(Payment.due_date >= start_date)
    if end_date:
        paid_stats = paid_stats.filter(Payment.due_date <= end_date)
    paid_result = paid_stats.first()

    pending_stats = db.query(
        func.count(Payment.id).label('count'),
        func.coalesce(func.sum(Payment.amount), 0).label('total')
    ).filter(Payment.status == 'pending')

    if start_date:
        pending_stats = pending_stats.filter(Payment.due_date >= start_date)
    if end_date:
        pending_stats = pending_stats.filter(Payment.due_date <= end_date)
    pending_result = pending_stats.first()

    overdue_stats = db.query(
        func.count(Payment.id).label('count'),
        func.coalesce(func.sum(Payment.amount), 0).label('total')
    ).filter(Payment.status == 'overdue')

    if start_date:
        overdue_stats = overdue_stats.filter(Payment.due_date >= start_date)
    if end_date:
        overdue_stats = overdue_stats.filter(Payment.due_date <= end_date)
    overdue_result = overdue_stats.first()

    # Total payments and amount
    total_stats = base_query.with_entities(
        func.count(Payment.id).label('count'),
        func.coalesce(func.sum(Payment.amount), 0).label('total')
    ).first()

    paid_count = paid_result.count if paid_result else 0
    paid_amount = float(paid_result.total) if paid_result else 0.0
    pending_count = pending_result.count if pending_result else 0
    pending_amount = float(pending_result.total) if pending_result else 0.0
    overdue_count = overdue_result.count if overdue_result else 0
    overdue_amount = float(overdue_result.total) if overdue_result else 0.0
    total_count = total_stats.count if total_stats else 0
    total_amount = float(total_stats.total) if total_stats else 0.0

    return {
        'total_payments': total_count,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'overdue_count': overdue_count,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'overdue_amount': overdue_amount,
        'collection_rate': (paid_amount / total_amount * 100) if total_amount > 0 else 0
    }


def get_tenant_statistics(db: Session) -> Dict[str, Any]:
    """Get tenant statistics"""
    total = db.query(Tenant).count()
    active = db.query(Tenant).filter(Tenant.status == 'active').count()
    inactive = db.query(Tenant).filter(Tenant.status == 'inactive').count()
    moved_out = db.query(Tenant).filter(Tenant.status == 'moved_out').count()

    return {
        'total_tenants': total,
        'active_tenants': active,
        'inactive_tenants': inactive,
        'moved_out_tenants': moved_out
    }


def is_payment_overdue(due_date: datetime) -> bool:
    """Check if payment is overdue"""
    return due_date < datetime.now(timezone.utc)


def days_until_due(due_date: datetime) -> int:
    """Calculate days until payment is due"""
    now = datetime.now(timezone.utc)
    delta = due_date - now
    return delta.days


def format_currency(amount: float, currency: str = "IDR") -> str:
    """Format amount as currency"""
    if currency == "IDR":
        return f"Rp {amount:,.0f}"
    return f"${amount:,.2f}"


def get_pagination_params(skip: int = 0, limit: int = 50) -> tuple:
    """Get and validate pagination parameters"""
    skip = max(0, skip)
    limit = min(max(1, limit), 100)  # Between 1 and 100
    return skip, limit


def apply_pagination(query, skip: int = 0, limit: int = 50):
    """Apply pagination to SQLAlchemy query"""
    skip, limit = get_pagination_params(skip, limit)
    return query.offset(skip).limit(limit)


def get_month_date_range(year: int, month: int) -> tuple:
    """Get start and end date for a specific month"""
    from datetime import date
    import calendar

    start_date = datetime(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime(year, month, last_day, 23, 59, 59)

    return start_date, end_date


def get_current_month_date_range() -> tuple:
    """Get start and end date for current month"""
    now = datetime.now(timezone.utc)
    return get_month_date_range(now.year, now.month)


def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Serialize datetime to ISO format string"""
    if dt is None:
        return None
    return dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)


def build_error_response(status_code: int, message: str, details: Optional[str] = None) -> Dict[str, Any]:
    """Build standardized error response"""
    response = {
        "status": "error",
        "status_code": status_code,
        "message": message
    }
    if details:
        response["details"] = details
    return response


def build_success_response(data: Any, message: str = None) -> Dict[str, Any]:
    """Build standardized success response"""
    response = {
        "status": "success",
        "data": data
    }
    if message:
        response["message"] = message
    return response
