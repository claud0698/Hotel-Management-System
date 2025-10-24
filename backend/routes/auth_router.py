"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from models import User
from schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from security import create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(lambda: None)):
    """Register a new admin user"""
    # Dependency injection will be fixed in main app.py
    from app import SessionLocal
    db = SessionLocal()
    try:
        # Check if username exists
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        # Check if email exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        # Create new user
        user = User(username=user_data.username, email=user_data.email)
        user.set_password(user_data.password)

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "message": "User created successfully",
            "user": user.to_dict()
        }
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with username and password"""
    from app import SessionLocal
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.username == credentials.username).first()

        if not user or not user.check_password(credentials.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Create token
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(days=30)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user.to_dict())
        )
    finally:
        db.close()


@router.get("/me", response_model=dict)
async def get_current_user_endpoint(current_user: dict = Depends(get_current_user)):
    """Get current logged-in user"""
    from app import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user["user_id"]).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {"user": user.to_dict()}
    finally:
        db.close()
