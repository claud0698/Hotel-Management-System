"""
Simple security utilities for authentication
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Simple in-memory token storage (for development)
# In production, use Redis or database
active_tokens = {}

# Token expiration time (in minutes)
TOKEN_EXPIRE_MINUTES = 60 * 16  # 16 hours (shift-based expiration)

security = HTTPBearer()


def create_access_token(user_id: int, username: str) -> str:
    """Create a simple access token with expiration"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    active_tokens[token] = {
        "user_id": user_id,
        "username": username,
        "expires_at": expires_at
    }
    return token


def verify_token(token: str) -> Optional[dict]:
    """Verify and get user data from token"""
    token_data = active_tokens.get(token)

    if not token_data:
        return None

    # Check if token has expired
    if datetime.now(timezone.utc) > token_data.get("expires_at"):
        # Token expired, remove it
        del active_tokens[token]
        return None

    return token_data


def revoke_token(token: str):
    """Revoke a token"""
    if token in active_tokens:
        del active_tokens[token]


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from token"""
    token = credentials.credentials
    user_data = verify_token(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_data
