"""
Room management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from models import Room
from schemas import RoomCreate, RoomUpdate, RoomResponse
from security import get_current_user
from database import get_db
from validators import (
    validate_room_number,
    validate_floor,
    validate_price,
    validate_room_type,
    validate_room_status
)

router = APIRouter()


@router.get("", response_model=dict)
async def get_rooms(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rooms with pagination and eager loading for performance"""
    # Eager load tenants to avoid N+1 queries
    query = db.query(Room).options(joinedload(Room.tenants))

    # Get total count for pagination metadata
    total = db.query(Room).count()

    # Apply pagination
    rooms = query.offset(skip).limit(limit).all()

    return {
        "rooms": [room.to_dict(include_tenant=True) for room in rooms],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{room_id}", response_model=dict)
async def get_room(
    room_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific room with eager loading"""
    room = db.query(Room).options(joinedload(Room.tenants)).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    return {"room": room.to_dict(include_tenant=True)}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new room"""
    # Validate inputs
    try:
        validated_room_number = validate_room_number(room_data.room_number)
        validated_floor = validate_floor(room_data.floor)
        validated_price = validate_price(room_data.monthly_rate)
        validated_room_type = validate_room_type(room_data.room_type)
        validated_status = validate_room_status(room_data.status)
    except HTTPException as e:
        raise e

    # Check if room number already exists
    if db.query(Room).filter(Room.room_number == validated_room_number).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room number already exists"
        )

    # Create room
    room = Room(
        room_number=validated_room_number,
        floor=validated_floor,
        room_type=validated_room_type,
        monthly_rate=validated_price,
        status=validated_status,
        amenities=room_data.amenities
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return {
        "message": "Room created successfully",
        "room": room.to_dict()
    }


@router.put("/{room_id}", response_model=dict)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a room"""
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    # Validate only provided fields
    try:
        update_data = room_data.model_dump(exclude_unset=True)

        if "room_number" in update_data and update_data["room_number"]:
            update_data["room_number"] = validate_room_number(update_data["room_number"])

        if "floor" in update_data:
            update_data["floor"] = validate_floor(update_data["floor"])

        if "monthly_rate" in update_data:
            update_data["monthly_rate"] = validate_price(update_data["monthly_rate"])

        if "room_type" in update_data:
            update_data["room_type"] = validate_room_type(update_data["room_type"])

        if "status" in update_data:
            update_data["status"] = validate_room_status(update_data["status"])
    except HTTPException as e:
        raise e

    # Check if new room number conflicts
    if "room_number" in update_data and update_data["room_number"] != room.room_number:
        if db.query(Room).filter(Room.room_number == update_data["room_number"]).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists"
            )

    # Update fields
    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)

    return {
        "message": "Room updated successfully",
        "room": room.to_dict()
    }


@router.delete("/{room_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_room(
    room_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a room"""
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    db.delete(room)
    db.commit()

    return {"message": "Room deleted"}
