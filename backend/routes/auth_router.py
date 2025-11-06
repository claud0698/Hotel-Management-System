"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import User
from schemas import UserLogin
from security import get_current_user, create_access_token
from database import get_db

router = APIRouter()


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint with proper authentication"""
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()

    # Check if user exists and password is correct
    if not user or not user.check_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(user.id, user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.get("/me", response_model=dict)
async def get_current_user_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current logged-in user"""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"user": user.to_dict()}
