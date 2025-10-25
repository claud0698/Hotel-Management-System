"""
User Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import User
from schemas import UserCreate, UserResponse, UserUpdate
from security import get_current_user


def get_db():
    """Get database session"""
    from app import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.get("", response_model=dict)
async def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all users"""
    users = db.query(User).all()
    return {
        "users": [user.to_dict() for user in users]
    }


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": user.to_dict()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Create new user
    new_user = User(username=user_data.username)
    new_user.set_password(user_data.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": new_user.to_dict()
    }


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update username if provided
    if user_data.username:
        # Check if new username already exists
        existing_user = db.query(User).filter(
            User.username == user_data.username,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        user.username = user_data.username

    # Update password if provided
    if user_data.password:
        user.set_password(user_data.password)

    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully",
        "user": user.to_dict()
    }


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a user"""
    # Prevent deleting yourself
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
