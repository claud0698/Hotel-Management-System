"""
Expense management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from models import Expense
from schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
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
async def get_expenses(
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses with optional filtering"""
    query = db.query(Expense)

    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(Expense.date >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(Expense.date <= end)

    expenses = query.all()
    return {
        "expenses": [expense.to_dict() for expense in expenses]
    }


@router.get("/{expense_id}", response_model=dict)
async def get_expense(
    expense_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    return {"expense": expense.to_dict()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    # Parse date
    date = datetime.fromisoformat(expense_data.date)

    # Create expense
    expense = Expense(
        date=date,
        category=expense_data.category,
        amount=expense_data.amount,
        description=expense_data.description,
        receipt_url=expense_data.receipt_url
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return {
        "message": "Expense created",
        "expense": expense.to_dict()
    }


@router.put("/{expense_id}", response_model=dict)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Update fields
    update_data = expense_data.model_dump(exclude_unset=True)

    # Handle date parsing
    if 'date' in update_data and update_data['date']:
        update_data['date'] = datetime.fromisoformat(update_data['date'])

    # Update expense
    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return {
        "message": "Expense updated",
        "expense": expense.to_dict()
    }


@router.delete("/{expense_id}", response_model=dict)
async def delete_expense(
    expense_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted"}
