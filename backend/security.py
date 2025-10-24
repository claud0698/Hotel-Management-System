"""
Simplified security - hardcoded access for development
"""

from typing import Optional
from fastapi import Depends, Request


async def get_current_user(request: Request = None) -> dict:
    """Hardcoded user for development - no authentication required"""
    return {"user_id": 1, "username": "admin"}
