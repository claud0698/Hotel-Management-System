"""
Payment management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from models import Payment
from schemas import PaymentCreate, PaymentUpdate, PaymentMarkPaid, ManualPaymentCreate, PaymentResponse
from security import get_current_user
from validators import (
    validate_payment_status,
    validate_amount,
    validate_date
)

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
        "payments": [payment.to_dict() for payment in payments]
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
    """Create a new payment"""
    # Validate inputs
    try:
        validated_amount = validate_amount(payment_data.amount, "Payment amount")
        validated_status = validate_payment_status(payment_data.status)
        validated_due_date = validate_date(payment_data.due_date, "Due date")
    except HTTPException as e:
        raise e

    # Verify tenant exists
    from models import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == payment_data.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with ID {payment_data.tenant_id} not found"
        )

    # Create payment
    payment = Payment(
        tenant_id=payment_data.tenant_id,
        amount=validated_amount,
        due_date=validated_due_date,
        status=validated_status,
        payment_method=payment_data.payment_method,
        receipt_number=payment_data.receipt_number,
        notes=payment_data.notes
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment created successfully",
        "payment": payment.to_dict()
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

    # Validate only provided fields
    try:
        update_data = payment_data.model_dump(exclude_unset=True)

        if "amount" in update_data:
            update_data["amount"] = validate_amount(update_data["amount"], "Payment amount")

        if "status" in update_data:
            update_data["status"] = validate_payment_status(update_data["status"])

        if "due_date" in update_data and update_data["due_date"]:
            update_data["due_date"] = validate_date(update_data["due_date"], "Due date")
    except HTTPException as e:
        raise e

    # Set paid_date if status is being set to paid
    if 'status' in update_data and update_data['status'] == 'paid' and not payment.paid_date:
        update_data['paid_date'] = datetime.now(timezone.utc)

    # Update payment
    for field, value in update_data.items():
        setattr(payment, field, value)

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment updated successfully",
        "payment": payment.to_dict()
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

    if payment.status == 'paid':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is already marked as paid"
        )

    payment.status = 'paid'
    payment.paid_date = datetime.now(timezone.utc)
    if mark_paid_data.payment_method:
        payment.payment_method = mark_paid_data.payment_method
    if mark_paid_data.receipt_number:
        payment.receipt_number = mark_paid_data.receipt_number

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment marked as paid successfully",
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

    return {"message": "Payment deleted"}


@router.post("/manual/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_manual_payment(
    payment_data: ManualPaymentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create payment by specifying number of months.
    Automatically calculates amount based on tenant's room rate and period.
    """
    from models import Tenant
    from dateutil.relativedelta import relativedelta

    # Verify tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == payment_data.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with ID {payment_data.tenant_id} not found"
        )

    # Verify tenant has a room assigned
    if not tenant.current_room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tenant {tenant.name} has no room assigned"
        )

    # Get the room to calculate amount
    from models import Room
    room = db.query(Room).filter(Room.id == tenant.current_room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room not found for tenant"
        )

    # Validate payment status
    try:
        validated_status = validate_payment_status(payment_data.status)
    except HTTPException as e:
        raise e

    # Calculate payment details
    monthly_rate = room.monthly_rate
    period_months = payment_data.period_months
    total_amount = monthly_rate * period_months

    # Calculate due date: add period_months to today
    today = datetime.now(timezone.utc)
    due_date = today + relativedelta(months=period_months)

    # Create payment
    payment = Payment(
        tenant_id=payment_data.tenant_id,
        amount=total_amount,
        due_date=due_date,
        status=validated_status,
        payment_method=payment_data.payment_method,
        receipt_number=payment_data.receipt_number,
        period_months=period_months,
        notes=payment_data.notes or f"Payment for {period_months} month(s)"
    )

    # If status is paid, set the paid_date
    if validated_status == 'paid':
        payment.paid_date = today

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": f"Manual payment created for {period_months} month(s)",
        "payment": payment.to_dict(),
        "details": {
            "tenant_name": tenant.name,
            "room_number": room.room_number,
            "monthly_rate": monthly_rate,
            "period_months": period_months,
            "total_amount": total_amount,
            "due_date": due_date.isoformat()
        }
    }
