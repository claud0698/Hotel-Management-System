"""
Guest Management Routes

Handles all guest-related endpoints:
- POST /api/guests - Create a new guest
- GET /api/guests - List guests with pagination and filters
- GET /api/guests/{id} - Get specific guest details
- PUT /api/guests/{id} - Update guest information
- DELETE /api/guests/{id} - Delete guest
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database import get_db
from models import Guest, RoomType
from schemas import GuestCreate, GuestUpdate, GuestResponse, GuestListResponse
from security import get_current_user

router = APIRouter(prefix="/api/guests", tags=["Guests"])


# ============== CREATE GUEST ==============

@router.post("", response_model=GuestResponse, status_code=201)
async def create_guest(
    guest_data: GuestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new guest.

    **Required Fields:**
    - full_name: Guest's full name

    **Optional Fields:**
    - email, phone, phone_country_code
    - id_type, id_number (for identification)
    - nationality, birth_date
    - is_vip, preferred_room_type_id
    - notes

    **Returns:** Created guest object with ID
    """
    # Check if email already exists (if provided)
    if guest_data.email:
        existing_guest = db.query(Guest).filter(Guest.email == guest_data.email).first()
        if existing_guest:
            raise HTTPException(
                status_code=400,
                detail=f"Guest with email {guest_data.email} already exists"
            )

    # Validate preferred_room_type_id if provided
    if guest_data.preferred_room_type_id:
        room_type = db.query(RoomType).filter(
            RoomType.id == guest_data.preferred_room_type_id
        ).first()
        if not room_type:
            raise HTTPException(
                status_code=404,
                detail=f"Room type with ID {guest_data.preferred_room_type_id} not found"
            )

    # Create new guest
    new_guest = Guest(**guest_data.model_dump())
    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)

    return new_guest.to_dict()


# ============== GET SINGLE GUEST ==============

@router.get("/{guest_id}", response_model=GuestResponse)
async def get_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get specific guest details by ID.

    **Parameters:**
    - guest_id: Guest ID

    **Returns:** Guest object with all details
    """
    guest = db.query(Guest).filter(Guest.id == guest_id).first()

    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {guest_id} not found")

    return guest.to_dict()


# ============== LIST GUESTS ==============

@router.get("", response_model=GuestListResponse)
async def list_guests(
    skip: int = Query(0, ge=0, description="Number of guests to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of guests to return"),
    is_vip: bool = Query(None, description="Filter by VIP status"),
    search: str = Query(None, description="Search by full name or email"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all guests with pagination and filtering.

    **Query Parameters:**
    - skip: Number of guests to skip (pagination offset)
    - limit: Maximum number of guests to return (default: 10, max: 100)
    - is_vip: Filter by VIP status (true/false)
    - search: Search by guest name or email (partial match)

    **Returns:** List of guests with total count and pagination info
    """
    query = db.query(Guest)

    # Apply VIP filter if provided
    if is_vip is not None:
        query = query.filter(Guest.is_vip == is_vip)

    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Guest.full_name.ilike(search_term),
                Guest.email.ilike(search_term)
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply pagination
    guests = query.offset(skip).limit(limit).all()

    # Convert to dictionaries
    guests_data = [guest.to_dict() for guest in guests]

    return {
        "guests": guests_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ============== UPDATE GUEST ==============

@router.put("/{guest_id}", response_model=GuestResponse)
async def update_guest(
    guest_id: int,
    guest_data: GuestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update guest information.

    **Parameters:**
    - guest_id: Guest ID to update

    **Request Body:** Fields to update (all optional)

    **Returns:** Updated guest object
    """
    guest = db.query(Guest).filter(Guest.id == guest_id).first()

    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {guest_id} not found")

    # Check if new email already exists (if being updated)
    if guest_data.email and guest_data.email != guest.email:
        existing_guest = db.query(Guest).filter(Guest.email == guest_data.email).first()
        if existing_guest:
            raise HTTPException(
                status_code=400,
                detail=f"Guest with email {guest_data.email} already exists"
            )

    # Validate preferred_room_type_id if being updated
    if guest_data.preferred_room_type_id and guest_data.preferred_room_type_id != guest.preferred_room_type_id:
        room_type = db.query(RoomType).filter(
            RoomType.id == guest_data.preferred_room_type_id
        ).first()
        if not room_type:
            raise HTTPException(
                status_code=404,
                detail=f"Room type with ID {guest_data.preferred_room_type_id} not found"
            )

    # Update only provided fields
    update_data = guest_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guest, field, value)

    db.commit()
    db.refresh(guest)

    return guest.to_dict()


# ============== DELETE GUEST ==============

@router.delete("/{guest_id}")
async def delete_guest(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a guest by ID.

    **Parameters:**
    - guest_id: Guest ID to delete

    **Note:** Consider soft delete to maintain reservation history integrity.

    **Returns:** Confirmation message
    """
    guest = db.query(Guest).filter(Guest.id == guest_id).first()

    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {guest_id} not found")

    # Check if guest has reservations
    if guest.reservations:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete guest with ID {guest_id} - guest has associated reservations. Consider soft delete instead."
        )

    db.delete(guest)
    db.commit()

    return {
        "message": f"Guest with ID {guest_id} deleted successfully"
    }


# ============== GET GUEST RESERVATIONS ==============

@router.get("/{guest_id}/reservations")
async def get_guest_reservations(
    guest_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all reservations for a specific guest.

    **Parameters:**
    - guest_id: Guest ID
    - skip: Pagination offset
    - limit: Maximum number of reservations to return

    **Returns:** List of guest's reservations with pagination info
    """
    guest = db.query(Guest).filter(Guest.id == guest_id).first()

    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {guest_id} not found")

    # Get reservations with pagination
    reservations = guest.reservations[skip:skip+limit]
    total = len(guest.reservations)

    # Convert to dictionaries
    reservations_data = [res.to_dict() for res in reservations]

    return {
        "guest_id": guest_id,
        "guest_name": guest.full_name,
        "reservations": reservations_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }
