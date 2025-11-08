"""
Reservation Management Routes

Handles all reservation-related endpoints:
- GET /api/reservations/availability - Check room availability for dates
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


# ============== AVAILABILITY CHECK ==============

@router.get("/availability")
async def check_availability(
    room_type_id: int = Query(..., description="Room type ID"),
    check_in_date: str = Query(..., description="Check-in date (YYYY-MM-DD)"),
    check_out_date: str = Query(..., description="Check-out date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Check room availability for a given date range and room type.

    **Query Parameters:**
    - room_type_id: Room type ID to check
    - check_in_date: Check-in date (YYYY-MM-DD)
    - check_out_date: Check-out date (YYYY-MM-DD)

    **Returns:**
    - available_rooms: Number of available rooms of this type
    - total_rooms: Total rooms of this type
    - is_available: Boolean indicating if rooms are available
    - message: Availability summary
    - room_type_name: Name of the room type
    """
    # Verify room type exists
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    if not room_type:
        raise HTTPException(status_code=404, detail=f"Room type with ID {room_type_id} not found")

    # Parse and validate dates
    try:
        check_in = datetime.fromisoformat(check_in_date).date() if isinstance(check_in_date, str) else check_in_date
        check_out = datetime.fromisoformat(check_out_date).date() if isinstance(check_out_date, str) else check_out_date
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    today = datetime.now().date()
    if check_in < today:
        raise HTTPException(status_code=400, detail="Check-in date cannot be in the past")
    if check_out <= check_in:
        raise HTTPException(status_code=400, detail="Check-out date must be after check-in date")

    # Count overlapping reservations (confirmed or checked_in)
    overlapping_reservations = db.query(Reservation).filter(
        Reservation.room_type_id == room_type_id,
        Reservation.status.in_(['confirmed', 'checked_in']),
        ~or_(
            Reservation.check_out_date <= check_in,
            Reservation.check_in_date >= check_out
        )
    ).count()

    total_rooms = db.query(Room).filter(Room.room_type_id == room_type_id).count()
    available_rooms = total_rooms - overlapping_reservations

    return {
        "room_type_id": room_type_id,
        "room_type_name": room_type.name,
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat(),
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "is_available": available_rooms > 0,
        "message": f"{available_rooms} of {total_rooms} rooms available" if total_rooms > 0 else "No rooms of this type"
    }


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

    # Convert date strings to date objects
    from datetime import date as date_type
    try:
        check_in = datetime.fromisoformat(reservation_data.check_in_date).date() if isinstance(reservation_data.check_in_date, str) else reservation_data.check_in_date
        check_out = datetime.fromisoformat(reservation_data.check_out_date).date() if isinstance(reservation_data.check_out_date, str) else reservation_data.check_out_date
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Validate dates
    today = datetime.now().date()
    if check_in < today:
        raise HTTPException(status_code=400, detail="Check-in date cannot be in the past")
    if check_out <= check_in:
        raise HTTPException(status_code=400, detail="Check-out date must be after check-in date")

    # Check availability: Count available rooms of this type for the date range
    # A room is available if it has no overlapping reservations
    overlapping_reservations = db.query(Reservation).filter(
        Reservation.room_type_id == reservation_data.room_type_id,
        Reservation.status.in_(['confirmed', 'checked_in']),
        # Overlapping condition: not (res.check_out <= check_in OR res.check_in >= check_out)
        ~or_(
            Reservation.check_out_date <= check_in,
            Reservation.check_in_date >= check_out
        )
    ).count()

    total_rooms_of_type = db.query(Room).filter(Room.room_type_id == reservation_data.room_type_id).count()
    available_rooms_of_type = total_rooms_of_type - overlapping_reservations

    if available_rooms_of_type <= 0:
        raise HTTPException(
            status_code=409,
            detail=f"No available rooms of type '{room_type.name}' for the selected dates ({check_in} to {check_out})"
        )

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
        deposit_amount=reservation_data.deposit_amount,
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
    require_payment: bool = Query(False, description="If true, check that at least partial payment is made"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Check in a guest and track which receptionist performed the check-in.

    **Parameters:**
    - reservation_id: Reservation ID
    - room_id: Room ID to assign to guest
    - require_payment: If true, requires partial/full payment before check-in (default: false)

    **Returns:** Confirmation with receptionist name, room assignment, and payment status

    **Tracked Information:**
    - checked_in_at: Timestamp of check-in
    - checked_in_by: User ID of receptionist
    - checked_in_by_name: Username of receptionist (for audit trail)
    - payment_status: Payment status at check-in time
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    if reservation.status == 'checked_in':
        raise HTTPException(status_code=400, detail="Guest is already checked in")

    if reservation.status == 'checked_out':
        raise HTTPException(status_code=400, detail="Guest has already checked out")

    # Optionally check payment before check-in
    if require_payment:
        total_paid = reservation.calculate_total_paid()
        if total_paid == 0:
            raise HTTPException(
                status_code=402,
                detail=f"Payment required. Total amount: {reservation.total_amount}, Paid: {total_paid}"
            )

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

    # Update room status to occupied (prevents double-booking)
    room.status = 'occupied'

    db.commit()
    db.refresh(reservation)

    # Get receptionist info for response
    receptionist = db.query(User).filter(User.id == current_user.get("user_id")).first()
    receptionist_name = receptionist.username if receptionist else "Unknown"

    # Calculate payment status
    total_paid = reservation.calculate_total_paid()
    balance = reservation.calculate_balance()
    if balance <= 0:
        payment_status = "fully_paid"
    elif total_paid > 0:
        payment_status = "partial_paid"
    else:
        payment_status = "unpaid"

    return {
        "message": "Guest checked in successfully",
        "reservation_id": reservation_id,
        "confirmation_number": reservation.confirmation_number,
        "guest_name": reservation.guest.full_name,
        "room_number": room.room_number,
        "room_type": room.room_type.name if room.room_type else "Unknown",
        "checked_in_at": reservation.checked_in_at.isoformat(),
        "checked_in_by": current_user.get("user_id"),
        "checked_in_by_name": receptionist_name,
        "total_amount": float(reservation.total_amount),
        "total_paid": total_paid,
        "balance": balance,
        "payment_status": payment_status,
    }


# ============== CHECK-OUT ==============

@router.post("/{reservation_id}/check-out")
async def check_out_guest(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Check out a guest and settle/return deposit.

    **Parameters:**
    - reservation_id: Reservation ID

    **Deposit Settlement Logic:**
    - IMPORTANT: If guest has a deposit (deposit_amount > 0), you MUST process the deposit return
    - Options:
      1. If guest paid more than total_amount (including deposit): Refund excess
      2. If guest balance remains unpaid: Deduct from deposit
      3. If guest balance is paid: Return full deposit
    - Mark deposit_returned_at when deposit is processed

    **Returns:** Confirmation with check-out time, deposit status, and balance owed
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    if reservation.status == 'checked_out':
        raise HTTPException(status_code=400, detail="Guest has already checked out")

    if reservation.status != 'checked_in':
        raise HTTPException(status_code=400, detail="Guest is not checked in")

    # Calculate final balance
    total_paid = reservation.calculate_total_paid()
    balance = reservation.calculate_balance()
    deposit_amount = float(reservation.deposit_amount) if reservation.deposit_amount else 0.0

    # Deposit settlement logic
    deposit_settlement = {
        "deposit_held": deposit_amount,
        "balance_owed": balance if balance > 0 else 0.0,
        "to_refund": 0.0,
        "settlement_note": ""
    }

    if deposit_amount > 0:
        if balance > 0:
            # Guest still owes money - deduct from deposit
            if deposit_amount >= balance:
                deposit_settlement["to_refund"] = deposit_amount - balance
                deposit_settlement["settlement_note"] = f"Deposit of {deposit_amount} used to cover {balance} balance. Refund {deposit_settlement['to_refund']}"
            else:
                # Deposit not enough to cover balance
                deposit_settlement["settlement_note"] = f"Deposit {deposit_amount} applied. Guest still owes {balance - deposit_amount}"
        else:
            # Guest paid everything - return full deposit
            deposit_settlement["to_refund"] = deposit_amount
            deposit_settlement["settlement_note"] = f"All charges paid. Returning full deposit of {deposit_amount}"

    # Update reservation
    reservation.status = 'checked_out'
    reservation.checked_out_at = datetime.utcnow()
    reservation.deposit_returned_at = datetime.utcnow()  # Mark deposit as processed

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
        "confirmation_number": reservation.confirmation_number,
        "guest_name": reservation.guest.full_name,
        "checked_out_at": reservation.checked_out_at.isoformat(),
        "total_amount": float(reservation.total_amount),
        "total_paid": total_paid,
        "balance_before_deposit": balance,
        "deposit_settlement": deposit_settlement,
        "final_balance_owed": max(0, balance - deposit_amount),  # Balance after deposit is applied
    }


# ============== BALANCE INQUIRY ==============

@router.get("/{reservation_id}/balance")
async def get_reservation_balance(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get balance information for a reservation (including deposit details).

    **Parameters**:
    - reservation_id: Reservation ID

    **Returns**:
    - Balance details including total, paid, and remaining amount
    - Deposit information: amount held and return status
    - Final balance after deposit is applied (for checkout)
    """
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if not reservation:
        raise HTTPException(status_code=404, detail=f"Reservation with ID {reservation_id} not found")

    total_amount = float(reservation.total_amount)
    total_paid = reservation.calculate_total_paid()
    balance = reservation.calculate_balance()
    deposit_amount = float(reservation.deposit_amount) if reservation.deposit_amount else 0.0

    # Determine payment status
    if balance <= 0:
        payment_status = "fully_paid"
    elif total_paid > 0:
        payment_status = "partial_paid"
    else:
        payment_status = "unpaid"

    # Calculate final balance after deposit is applied
    final_balance_after_deposit = max(0, balance - deposit_amount)

    return {
        "reservation_id": reservation_id,
        "confirmation_number": reservation.confirmation_number,
        "guest_name": reservation.guest.full_name,
        "total_amount": total_amount,
        "total_paid": total_paid,
        "balance": balance,
        "deposit_amount": deposit_amount,
        "deposit_returned_at": reservation.deposit_returned_at.isoformat() if reservation.deposit_returned_at else None,
        "final_balance_after_deposit": final_balance_after_deposit,
        "payment_status": payment_status,
        "reservation_status": reservation.status,
    }
