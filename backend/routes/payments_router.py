"""
Payment management routes for Hotel Management System

Handles all payment-related endpoints:
- POST /api/payments - Record new payment
- GET /api/payments - List payments with filtering
- GET /api/payments/{id} - Get payment details
- PUT /api/payments/{id} - Update payment
- DELETE /api/payments/{id} - Delete/void payment
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

from models import Payment, Reservation
from schemas import PaymentCreate, PaymentUpdate
from security import get_current_user
from database import get_db

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.get("", response_model=dict)
async def get_payments(
    reservation_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payments with optional filtering and pagination"""
    query = db.query(Payment)

    if reservation_id:
        query = query.filter(Payment.reservation_id == reservation_id)
    if status_filter:
        query = query.filter(Payment.status == status_filter)

    # Get total count with filters applied
    total = query.count()

    # Apply pagination
    payments = query.offset(skip).limit(limit).all()

    return {
        "payments": [payment.to_dict() for payment in payments],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{payment_id}", response_model=dict)
async def get_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return {"payment": payment.to_dict()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a new payment for a reservation.

    **Request Body**:
    - reservation_id: Reservation ID (required)
    - amount: Payment amount (required, > 0)
    - payment_method: cash, credit_card, debit_card, bank_transfer, e_wallet, other
    - payment_date: Date of payment (required)
    - reference_number: Optional reference (card number, transfer ID, etc.)
    - notes: Optional notes

    **Returns**: Created payment with ID and details
    """
    # Verify reservation exists
    reservation = db.query(Reservation).filter(
        Reservation.id == payment_data.reservation_id
    ).first()

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {payment_data.reservation_id} not found"
        )

    # Create payment
    payment = Payment(
        reservation_id=payment_data.reservation_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        payment_type=payment_data.payment_type,
        payment_date=payment_data.payment_date,
        reference_number=payment_data.reference_number,
        notes=payment_data.notes,
        created_by=current_user.get("user_id")
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment recorded successfully",
        "payment": payment.to_dict()
    }


@router.put("/{payment_id}", response_model=dict)
async def update_payment(
    payment_id: int,
    payment_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Update fields
    for field, value in payment_data.items():
        if value is not None and hasattr(payment, field):
            setattr(payment, field, value)

    # Set paid_at if status is being set to paid
    if payment_data.get("status") == "paid" and payment.status != "paid":
        payment.paid_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment updated successfully",
        "payment": payment.to_dict()
    }


@router.delete("/{payment_id}", response_model=dict)
async def delete_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    db.delete(payment)
    db.commit()

    return {"message": "Payment deleted successfully"}
