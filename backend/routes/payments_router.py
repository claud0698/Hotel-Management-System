"""
Payment management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from models import Payment
from schemas import PaymentCreate, PaymentUpdate, PaymentMarkPaid, PaymentResponse
from security import get_current_user

router = APIRouter()


def get_db():
    """Get database session"""
    from app import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=dict)
async def get_payments(
    tenant_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payments with optional filtering"""
    query = db.query(Payment)

    if tenant_id:
        query = query.filter(Payment.tenant_id == tenant_id)
    if status_filter:
        query = query.filter(Payment.status == status_filter)

    payments = query.all()
    return {
        "payments": [PaymentResponse.model_validate(payment) for payment in payments]
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

    return {"payment": PaymentResponse.model_validate(payment)}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment"""
    # Parse due_date
    due_date = datetime.fromisoformat(payment_data.due_date)

    # Create payment
    payment = Payment(
        tenant_id=payment_data.tenant_id,
        amount=payment_data.amount,
        due_date=due_date,
        status=payment_data.status,
        payment_method=payment_data.payment_method,
        receipt_number=payment_data.receipt_number,
        notes=payment_data.notes
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment created",
        "payment": PaymentResponse.model_validate(payment)
    }


@router.put("/{payment_id}", response_model=dict)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
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
    update_data = payment_data.model_dump(exclude_unset=True)

    # Handle due_date parsing
    if 'due_date' in update_data and update_data['due_date']:
        update_data['due_date'] = datetime.fromisoformat(update_data['due_date'])

    # Set paid_date if status is being set to paid
    if 'status' in update_data and update_data['status'] == 'paid' and not payment.paid_date:
        update_data['paid_date'] = datetime.utcnow()

    # Update payment
    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment updated",
        "payment": PaymentResponse.model_validate(payment)
    }


@router.post("/{payment_id}/mark-paid", response_model=dict)
async def mark_payment_paid(
    payment_id: int,
    mark_paid_data: PaymentMarkPaid,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a payment as paid"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    payment.status = 'paid'
    payment.paid_date = datetime.utcnow()
    if mark_paid_data.payment_method:
        payment.payment_method = mark_paid_data.payment_method
    if mark_paid_data.receipt_number:
        payment.receipt_number = mark_paid_data.receipt_number

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment marked as paid",
        "payment": PaymentResponse.model_validate(payment)
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

    return {"message": "Payment deleted"}
