"""
Utility functions for Kos Management Dashboard
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Payment, Room, Tenant


def calculate_occupancy_rate(db: Session) -> float:
    """Calculate overall occupancy rate"""
    total_rooms = db.query(Room).count()
    if total_rooms == 0:
        return 0.0

    occupied_rooms = db.query(Room).filter(Room.status == 'occupied').count()
    return round((occupied_rooms / total_rooms) * 100, 2)


def get_room_occupancy_details(db: Session) -> Dict[str, Any]:
    """Get detailed room occupancy statistics"""
    total = db.query(Room).count()
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
    """Get payment statistics"""
    query = db.query(Payment)

    if start_date:
        query = query.filter(Payment.due_date >= start_date)
    if end_date:
        query = query.filter(Payment.due_date <= end_date)

    all_payments = query.all()
    paid = [p for p in all_payments if p.status == 'paid']
    pending = [p for p in all_payments if p.status == 'pending']
    overdue = [p for p in all_payments if p.status == 'overdue']

    total_amount = sum(p.amount for p in all_payments)
    paid_amount = sum(p.amount for p in paid)
    pending_amount = sum(p.amount for p in pending)
    overdue_amount = sum(p.amount for p in overdue)

    return {
        'total_payments': len(all_payments),
        'paid_count': len(paid),
        'pending_count': len(pending),
        'overdue_count': len(overdue),
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
