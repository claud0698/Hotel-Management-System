"""
Room management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import Room
from schemas import RoomCreate, RoomUpdate, RoomResponse
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
async def get_rooms(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rooms"""
    rooms = db.query(Room).all()
    return {
        "rooms": [room.to_dict() for room in rooms]
    }


@router.get("/{room_id}", response_model=dict)
async def get_room(
    room_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific room"""
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    return {"room": room.to_dict()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new room"""
    # Check if room number already exists
    if db.query(Room).filter(Room.room_number == room_data.room_number).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room number already exists"
        )

    # Create room
    room = Room(
        room_number=room_data.room_number,
        floor=room_data.floor,
        room_type=room_data.room_type,
        monthly_rate=room_data.monthly_rate,
        status=room_data.status,
        amenities=room_data.amenities
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return {
        "message": "Room created",
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

    # Check if new room number conflicts
    if room_data.room_number and room_data.room_number != room.room_number:
        if db.query(Room).filter(Room.room_number == room_data.room_number).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists"
            )

    # Update fields
    update_data = room_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)

    return {
        "message": "Room updated",
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
