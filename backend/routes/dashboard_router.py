"""
Dashboard and analytics routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Optional

from models import Room, Tenant, Payment, Expense
from schemas import DashboardMetrics, DashboardSummary
from security import get_current_user
from database import get_db
from utils import (
    calculate_occupancy_rate,
    get_room_occupancy_details,
    get_payment_statistics,
    get_tenant_statistics,
    get_current_month_date_range
)

router = APIRouter()


@router.get("/metrics", response_model=DashboardMetrics)
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

    # Use utility functions for calculations (pass date range for historical occupancy)
    room_details = get_room_occupancy_details(db, start, end)
    payment_stats = get_payment_statistics(db, start, end)

    # Expenses - use database aggregation instead of loading all records
    total_expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.date >= start,
        Expense.date < end
    ).scalar() or 0.0

    # Overdue payments - use database aggregation
    overdue_stats = db.query(
        func.count(Payment.id).label('count'),
        func.coalesce(func.sum(Payment.amount), 0).label('total')
    ).filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.now(timezone.utc)
    ).first()

    overdue_count = overdue_stats.count if overdue_stats else 0
    overdue_amount = float(overdue_stats.total) if overdue_stats else 0.0

    # Calculate net profit
    net_profit = payment_stats['paid_amount'] - total_expenses

    return DashboardMetrics(
        total_rooms=room_details['total_rooms'],
        occupied_rooms=room_details['occupied_rooms'],
        available_rooms=room_details['available_rooms'],
        occupancy_rate=room_details['occupancy_rate'],
        total_income=payment_stats['paid_amount'],
        total_expenses=total_expenses,
        net_profit=net_profit,
        overdue_count=overdue_count,
        overdue_amount=overdue_amount,
        pending_count=payment_stats['pending_count'],
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

    # Overdue tenants - Use JOIN to avoid N+1 query problem
    overdue_data = db.query(Payment, Tenant).join(
        Tenant, Payment.tenant_id == Tenant.id
    ).filter(
        Payment.status == 'pending',
        Payment.due_date < datetime.now(timezone.utc)
    ).all()

    overdue_tenants = [
        {
            'tenant': tenant.to_dict(),
            'payment': payment.to_dict()
        }
        for payment, tenant in overdue_data
    ]

    return DashboardSummary(
        recent_payments=[p.to_dict() for p in recent_payments],
        recent_expenses=[e.to_dict() for e in recent_expenses],
        overdue_tenants=overdue_tenants
    )
