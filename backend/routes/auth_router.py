"""
Authentication routes (simplified for development)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models import User
from schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from security import get_current_user

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_current_user_endpoint(current_user: dict = Depends(get_current_user)):
    """Get current logged-in user (hardcoded for dev)"""
    return {
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@kos.local",
            "created_at": "2025-10-24T00:00:00"
        }
    }


@router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin):
    """Login endpoint (simplified - no auth check for dev)"""
    return {
        "access_token": "dev-token-no-validation",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@kos.local",
            "created_at": "2025-10-24T00:00:00"
        }
    }
