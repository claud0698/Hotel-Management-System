"""
Input validators for Kos Management Dashboard
"""

from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status


def validate_room_number(room_number: str) -> str:
    """Validate room number format"""
    if not room_number or not isinstance(room_number, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room number must be a non-empty string"
        )
    if len(room_number) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room number must be 20 characters or less"
        )
    return room_number.strip()


def validate_floor(floor: int) -> int:
    """Validate floor number"""
    if not isinstance(floor, int) or floor < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Floor must be a non-negative integer"
        )
    if floor > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Floor number seems too high (max 100)"
        )
    return floor


def validate_price(price: float) -> float:
    """Validate monthly rate"""
    if price is None or price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monthly rate must be a positive number"
        )
    if price > 999_999_999:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monthly rate is unreasonably high"
        )
    return float(price)


def validate_room_type(room_type: str) -> str:
    """Validate room type"""
    valid_types = ['single', 'double', 'suite', 'studio']
    if room_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room type must be one of: {', '.join(valid_types)}"
        )
    return room_type.lower()


def validate_room_status(status: str) -> str:
    """Validate room status"""
    valid_statuses = ['available', 'occupied', 'maintenance', 'reserved']
    if status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room status must be one of: {', '.join(valid_statuses)}"
        )
    return status.lower()


def validate_tenant_name(name: str) -> str:
    """Validate tenant name"""
    if not name or not isinstance(name, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant name must be a non-empty string"
        )
    if len(name) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant name must be at least 3 characters"
        )
    if len(name) > 120:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant name must be 120 characters or less"
        )
    return name.strip()


def validate_tenant_status(status: str) -> str:
    """Validate tenant status"""
    valid_statuses = ['active', 'inactive', 'moved_out', 'on_hold']
    if status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tenant status must be one of: {', '.join(valid_statuses)}"
        )
    return status.lower()


def validate_payment_status(status: str) -> str:
    """Validate payment status"""
    valid_statuses = ['pending', 'paid', 'overdue', 'cancelled']
    if status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment status must be one of: {', '.join(valid_statuses)}"
        )
    return status.lower()


def validate_expense_category(category: str) -> str:
    """Validate expense category"""
    valid_categories = [
        'utilities', 'maintenance', 'cleaning', 'supplies',
        'repairs', 'insurance', 'taxes', 'other'
    ]
    if category.lower() not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expense category must be one of: {', '.join(valid_categories)}"
        )
    return category.lower()


def validate_amount(amount: float, field_name: str = "Amount") -> float:
    """Validate monetary amount"""
    if amount is None or amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be a non-negative number"
        )
    if amount > 999_999_999:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} is unreasonably high"
        )
    return float(amount)


def validate_date(date_str: Optional[str], field_name: str = "Date") -> Optional[datetime]:
    """Validate date format"""
    if date_str is None:
        return None

    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be in ISO format (YYYY-MM-DD)"
        )


def validate_email(email: str) -> str:
    """Validate email format"""
    if not email:
        return None

    if '@' not in email or '.' not in email.split('@')[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    return email.lower().strip()


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """Validate phone format"""
    if not phone:
        return None

    if len(phone) < 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be at least 7 digits"
        )

    return phone.strip()
