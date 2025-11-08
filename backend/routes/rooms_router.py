"""
Room management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from models import Room, RoomType
from schemas import RoomCreate, RoomUpdate
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


@router.get("/types", response_model=dict)
async def get_room_types(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available room types"""
    room_types = db.query(RoomType).filter(RoomType.is_active == True).all()

    return {
        "room_types": [
            {
                "id": rt.id,
                "code": rt.code,
                "name": rt.name,
                "description": rt.description,
                "default_rate": float(rt.default_rate) if rt.default_rate else 0,
                "amenities": rt.amenities,
                "bed_config": rt.bed_config,
                "max_occupancy": rt.max_occupancy,
            }
            for rt in room_types
        ]
    }


def _format_room_response(room: Room) -> dict:
    """Format room object for API response"""
    return {
        "id": room.id,
        "room_number": room.room_number,
        "floor": room.floor,
        "room_type_id": room.room_type_id,
        "room_type": room.room_type.code if room.room_type else None,
        "room_type_name": room.room_type.name if room.room_type else None,
        "status": room.status,
        "view_type": room.view_type,
        "notes": room.notes,
        "custom_rate": float(room.custom_rate) if room.custom_rate else None,
        "nightly_rate": float(room.custom_rate) if room.custom_rate
        else (float(room.room_type.default_rate) if room.room_type else None),
        "amenities": room.room_type.amenities if room.room_type else None,
        "is_active": room.is_active,
        "created_at": room.created_at.isoformat() if room.created_at else None,
        "updated_at": room.updated_at.isoformat() if room.updated_at else None,
    }


@router.get("", response_model=dict)
async def get_rooms(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rooms with pagination"""
    # Get total count for pagination metadata
    total = db.query(Room).count()

    # Query rooms with room_type relationship loaded
    rooms = (db.query(Room)
             .options(joinedload(Room.room_type))
             .offset(skip).limit(limit).all())

    return {
        "rooms": [_format_room_response(room) for room in rooms],
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
    room = (db.query(Room)
            .options(joinedload(Room.room_type))
            .filter(Room.id == room_id).first())

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    return {"room": _format_room_response(room)}


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

    # Find room_type by code
    room_type_obj = db.query(RoomType).filter(
        RoomType.code == validated_room_type
    ).first()

    if not room_type_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room type '{validated_room_type}' not found"
        )

    # Create room with custom_rate (monthly rate override)
    room = Room(
        room_number=validated_room_number,
        floor=validated_floor,
        room_type_id=room_type_obj.id,
        custom_rate=validated_price,
        status=validated_status,
        amenities=room_data.amenities
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return {
        "message": "Room created successfully",
        "room": _format_room_response(room)
    }


@router.put("/{room_id}", response_model=dict)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a room"""
    room = (db.query(Room)
            .options(joinedload(Room.room_type))
            .filter(Room.id == room_id).first())

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    # Validate only provided fields
    try:
        update_data = room_data.model_dump(exclude_unset=True)

        if "room_number" in update_data and update_data["room_number"]:
            update_data["room_number"] = validate_room_number(
                update_data["room_number"]
            )

        if "floor" in update_data:
            update_data["floor"] = validate_floor(update_data["floor"])

        if "monthly_rate" in update_data:
            update_data["monthly_rate"] = validate_price(
                update_data["monthly_rate"]
            )

        if "room_type" in update_data:
            update_data["room_type"] = validate_room_type(
                update_data["room_type"]
            )

        if "status" in update_data:
            update_data["status"] = validate_room_status(
                update_data["status"]
            )
    except HTTPException as e:
        raise e

    # Check if new room number conflicts
    if ("room_number" in update_data and
            update_data["room_number"] != room.room_number):
        if (db.query(Room)
                .filter(Room.room_number == update_data["room_number"])
                .first()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room number already exists"
            )

    # Handle room_type separately (map code to room_type_id)
    if "room_type" in update_data:
        room_type_code = update_data.pop("room_type")
        room_type_obj = db.query(RoomType).filter(
            RoomType.code == room_type_code
        ).first()
        if not room_type_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room type '{room_type_code}' not found"
            )
        update_data["room_type_id"] = room_type_obj.id

    # Handle monthly_rate -> custom_rate mapping
    if "monthly_rate" in update_data:
        update_data["custom_rate"] = update_data.pop("monthly_rate")

    # Update fields
    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)

    return {
        "message": "Room updated successfully",
        "room": _format_room_response(room)
    }


@router.delete("/{room_id}", response_model=dict,
               status_code=status.HTTP_200_OK)
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
