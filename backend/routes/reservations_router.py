"""
Reservation Management Routes

Handles all reservation-related endpoints:
- POST /api/reservations - Create reservation
- GET /api/reservations - List reservations
- GET /api/reservations/{id} - Get reservation details
- PUT /api/reservations/{id} - Update reservation
- DELETE /api/reservations/{id} - Cancel reservation
- POST /api/reservations/{id}/check-in - Guest check-in with receptionist tracking
- POST /api/reservations/{id}/check-out - Guest check-out
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime

from database import get_db
from models import Reservation, Guest, Room, RoomType, User
from schemas import (
    ReservationCreate, ReservationUpdate, ReservationResponse,
    ReservationListResponse
)
from security import get_current_user

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


# ============== CREATE RESERVATION ==============

@router.post("", response_model=ReservationResponse, status_code=201)
async def create_reservation(
    reservation_data: "ReservationCreate",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new reservation.

    **Required Fields:**
    - guest_id: Guest ID
    - room_type_id: Room type ID
    - check_in_date: Check-in date (YYYY-MM-DD)
    - check_out_date: Check-out date (YYYY-MM-DD)
    - rate_per_night: Rate per night

    **Returns:** Created reservation with confirmation number
    """
    # Verify guest exists
    guest = db.query(Guest).filter(Guest.id == reservation_data.guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {reservation_data.guest_id} not found")

    # Verify room type exists
    room_type = db.query(RoomType).filter(RoomType.id == reservation_data.room_type_id).first()
    if not room_type:
        raise HTTPException(status_code=404, detail=f"Room type with ID {reservation_data.room_type_id} not found")

    # TODO: Check availability and prevent double-booking
    # This is a placeholder - implement availability checking logic

    # Create new reservation
    import secrets
    confirmation_number = secrets.token_hex(5).upper()

    new_reservation = Reservation(
        confirmation_number=confirmation_number,
        guest_id=reservation_data.guest_id,
        room_type_id=reservation_data.room_type_id,
        check_in_date=reservation_data.check_in_date,
        check_out_date=reservation_data.check_out_date,
        adults=reservation_data.adults,
        children=reservation_data.children,
        rate_per_night=reservation_data.rate_per_night,
        subtotal=reservation_data.subtotal,
        discount_amount=reservation_data.discount_amount,
        total_amount=reservation_data.total_amount,
        special_requests=reservation_data.special_requests,
        created_by=current_user.get("user_id"),
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)

    return new_reservation.to_dict()


# ============== LIST RESERVATIONS ==============

@router.get("", response_model=ReservationListResponse)
async def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query(None, description="Filter by status: confirmed, checked_in, checked_out, cancelled"),
    guest_id: int = Query(None, description="Filter by guest ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all reservations with pagination and filters.

    **Query Parameters:**
    - skip: Number of records to skip
    - limit: Maximum number of records to return
    - status: Filter by reservation status
    - guest_id: Filter by guest ID

    **Returns:** List of reservations with pagination info
    """
    query = db.query(Reservation)

    if status:
        query = query.filter(Reservation.status == status)

    if guest_id:
        query = query.filter(Reservation.guest_id == guest_id)

    total = query.count()
    reservations = query.offset(skip).limit(limit).all()

    reservations_data = [res.to_dict() for res in reservations]

    return {
        "reservations": reservations_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ============== GET SINGLE RESERVATION ==============

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get specific reservation details by ID.

    **Parameters:**
    - reservation_id: Reservation ID

    **Returns:** Reservation details including check-in info
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    return reservation.to_dict()


# ============== UPDATE RESERVATION ==============

@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: int,
    reservation_data: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update reservation information.

    **Parameters:**
    - reservation_id: Reservation ID to update

    **Returns:** Updated reservation
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    # Update only provided fields
    update_data = reservation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reservation, field, value)

    reservation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reservation)

    return reservation.to_dict()


# ============== DELETE/CANCEL RESERVATION ==============

@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Cancel a reservation by changing status to 'cancelled'.

    **Parameters:**
    - reservation_id: Reservation ID to cancel

    **Returns:** Confirmation message
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    reservation.status = 'cancelled'
    reservation.updated_at = datetime.utcnow()
    db.commit()

    return {"message": f"Reservation {reservation_id} cancelled successfully"}


# ============== CHECK-IN WITH RECEPTIONIST TRACKING ==============

@router.post("/{reservation_id}/check-in")
async def check_in_guest(
    reservation_id: int,
    room_id: int = Query(..., description="Room ID to assign to guest"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Check in a guest and track which receptionist performed the check-in.

    **Parameters:**
    - reservation_id: Reservation ID
    - room_id: Room ID to assign to guest

    **Request Body:**
    - room_id: Specific room to assign

    **Returns:** Confirmation with receptionist name and check-in time

    **Tracked Information:**
    - checked_in_at: Timestamp of check-in
    - checked_in_by: User ID of receptionist
    - checked_in_by_name: Username of receptionist (for audit trail)
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    if reservation.status == 'checked_in':
        raise HTTPException(status_code=400, detail="Guest is already checked in")

    if reservation.status == 'checked_out':
        raise HTTPException(status_code=400, detail="Guest has already checked out")

    # Verify room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Room with ID {room_id} not found")

    # Check room is available
    if room.status != 'available':
        raise HTTPException(status_code=400, detail=f"Room {room.room_number} is not available ({room.status})")

    # Update reservation with check-in info
    reservation.room_id = room_id
    reservation.status = 'checked_in'
    reservation.checked_in_at = datetime.utcnow()
    reservation.checked_in_by = current_user.get("user_id")  # Store receptionist ID

    # Update room status
    room.status = 'occupied'

    db.commit()
    db.refresh(reservation)

    # Get receptionist info for response
    receptionist = db.query(User).filter(User.id == current_user.get("user_id")).first()
    receptionist_name = receptionist.username if receptionist else "Unknown"

    return {
        "message": "Guest checked in successfully",
        "reservation_id": reservation_id,
        "guest_name": reservation.guest.full_name,
        "room_number": room.room_number,
        "checked_in_at": reservation.checked_in_at.isoformat(),
        "checked_in_by": current_user.get("user_id"),
        "checked_in_by_name": receptionist_name,
    }


# ============== CHECK-OUT ==============

@router.post("/{reservation_id}/check-out")
async def check_out_guest(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Check out a guest.

    **Parameters:**
    - reservation_id: Reservation ID

    **Returns:** Confirmation with check-out time
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    if reservation.status == 'checked_out':
        raise HTTPException(status_code=400, detail="Guest has already checked out")

    if reservation.status != 'checked_in':
        raise HTTPException(status_code=400, detail="Guest is not checked in")

    # Update reservation
    reservation.status = 'checked_out'
    reservation.checked_out_at = datetime.utcnow()

    # Update room status
    if reservation.room_id:
        room = db.query(Room).filter(Room.id == reservation.room_id).first()
        if room:
            room.status = 'available'

    db.commit()
    db.refresh(reservation)

    return {
        "message": "Guest checked out successfully",
        "reservation_id": reservation_id,
        "guest_name": reservation.guest.full_name,
        "checked_out_at": reservation.checked_out_at.isoformat(),
        "total_amount": float(reservation.total_amount),
        "total_paid": reservation.calculate_total_paid(),
        "balance": reservation.calculate_balance(),
    }
