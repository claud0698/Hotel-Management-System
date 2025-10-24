"""
Dashboard and analytics routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from models import Room, Tenant, Payment, Expense
from schemas import DashboardMetrics, DashboardSummary
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


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics"""
    # Default to current month
    now = datetime.utcnow()
    if not start_date:
        start = datetime(now.year, now.month, 1)
    else:
        start = datetime.fromisoformat(start_date)

    if not end_date:
        if now.month == 12:
            end = datetime(now.year + 1, 1, 1)
        else:
            end = datetime(now.year, now.month + 1, 1)
    else:
        end = datetime.fromisoformat(end_date)

    # Calculate metrics
    total_rooms = db.query(Room).count()
    occupied_rooms = db.query(Room).filter(Room.status == 'occupied').count()
    available_rooms = db.query(Room).filter(Room.status == 'available').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    # Income
    paid_payments = db.query(Payment).filter(
        Payment.status == 'paid',
        Payment.paid_date >= start,
        Payment.paid_date < end
    ).all()
    total_income = sum(p.amount for p in paid_payments)

    # Expenses
    expenses = db.query(Expense).filter(
        Expense.date >= start,
        Expense.date < end
    ).all()
    total_expenses = sum(e.amount for e in expenses)

    # Overdue payments
    overdue_payments = db.query(Payment).filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.utcnow()
    ).all()
    overdue_count = len(overdue_payments)
    overdue_amount = sum(p.amount for p in overdue_payments)

    # Pending payments
    pending_payments = db.query(Payment).filter(Payment.status == 'pending').all()

    net_profit = total_income - total_expenses

    return DashboardMetrics(
        total_rooms=total_rooms,
        occupied_rooms=occupied_rooms,
        available_rooms=available_rooms,
        occupancy_rate=round(occupancy_rate, 2),
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=net_profit,
        overdue_count=overdue_count,
        overdue_amount=overdue_amount,
        pending_count=len(pending_payments),
        start_date=start.isoformat(),
        end_date=end.isoformat()
    )


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary data for dashboard"""
    # Recent payments
    recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(5).all()

    # Recent expenses
    recent_expenses = db.query(Expense).order_by(Expense.created_at.desc()).limit(5).all()

    # Overdue tenants
    overdue_payments = db.query(Payment).filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.utcnow()
    ).all()

    overdue_tenants = []
    for payment in overdue_payments:
        tenant = db.query(Tenant).filter(Tenant.id == payment.tenant_id).first()
        if tenant:
            overdue_tenants.append({
                'tenant': tenant.to_dict(),
                'payment': payment.to_dict()
            })

    return DashboardSummary(
        recent_payments=[p.to_dict() for p in recent_payments],
        recent_expenses=[e.to_dict() for e in recent_expenses],
        overdue_tenants=overdue_tenants
    )
