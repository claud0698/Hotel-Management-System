"""
Expense management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from models import Expense
from schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from security import get_current_user
from database import get_db
from validators import (
    validate_expense_category,
    validate_amount,
    validate_date
)

router = APIRouter()


@router.get("", response_model=dict)
async def get_expenses(
    category: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses with optional filtering and pagination"""
    query = db.query(Expense)

    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(Expense.date >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(Expense.date <= end)

    # Get total count with filters applied
    total = query.count()

    # Apply pagination
    expenses = query.offset(skip).limit(limit).all()

    return {
        "expenses": [expense.to_dict() for expense in expenses],
        "total": total,
        "skip": skip,
        "limit": limit
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
    # Validate inputs
    try:
        validated_category = validate_expense_category(expense_data.category)
        validated_amount = validate_amount(expense_data.amount, "Expense amount")
        validated_date = validate_date(expense_data.date, "Expense date")
    except HTTPException as e:
        raise e

    # Create expense
    expense = Expense(
        date=validated_date,
        category=validated_category,
        amount=validated_amount,
        description=expense_data.description,
        receipt_url=expense_data.receipt_url
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return {
        "message": "Expense created successfully",
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

    # Validate only provided fields
    try:
        update_data = expense_data.model_dump(exclude_unset=True)

        if "category" in update_data:
            update_data["category"] = validate_expense_category(update_data["category"])

        if "amount" in update_data:
            update_data["amount"] = validate_amount(update_data["amount"], "Expense amount")

        if "date" in update_data and update_data["date"]:
            update_data["date"] = validate_date(update_data["date"], "Expense date")
    except HTTPException as e:
        raise e

    # Update expense
    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return {
        "message": "Expense updated successfully",
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
