"""
Guest Management Routes

Handles all guest-related endpoints:
- POST /api/guests - Create a new guest (requires full_name, id_type, id_number)
- GET /api/guests - List guests with pagination and filters
- GET /api/guests/{id} - Get specific guest details
- PUT /api/guests/{id} - Update guest information
- DELETE /api/guests/{id} - Delete guest
- POST /api/guests/{id}/upload-id-photo - Upload guest ID photo
- GET /api/guests/{id}/photos - Get guest's ID photos
"""

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import os

from database import get_db
from models import Guest, RoomType, GuestImage, User
from schemas import GuestCreate, GuestUpdate, GuestResponse, GuestListResponse, GuestImageResponse
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
    Create a new guest. Receptionist will photocopy ID and input details.

    **REQUIRED Fields:**
    - full_name: Guest's full name
    - id_type: Type of ID (passport, driver_license, national_id, etc.)
    - id_number: ID document number

    **Optional Fields:**
    - email, phone, phone_country_code
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


# ============== UPLOAD GUEST ID PHOTO ==============

@router.post("/{guest_id}/upload-id-photo", response_model=GuestImageResponse, status_code=201)
async def upload_guest_id_photo(
    guest_id: int,
    image_type: str = Query("id_photo", description="Type of photo: id_photo, passport_photo, license_photo, etc."),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload guest ID photo/document photo. Receptionist uploads scanned/photographed ID.

    **Parameters:**
    - guest_id: Guest ID
    - image_type: Type of photo (id_photo, passport_photo, license_photo, etc.)
    - file: Image file (JPEG, PNG, PDF)

    **Returns:** Guest image metadata with file path
    """
    # Verify guest exists
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {guest_id} not found")

    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: JPEG, PNG, PDF. Got: {file.content_type}"
        )

    # Create uploads directory if it doesn't exist
    upload_dir = f"uploads/guests/{guest_id}"
    os.makedirs(upload_dir, exist_ok=True)

    # Save file with unique name
    file_extension = file.filename.split(".")[-1]
    safe_filename = f"{image_type}_{guest_id}_{os.urandom(4).hex()}.{file_extension}"
    file_path = os.path.join(upload_dir, safe_filename)

    # Read and save file
    file_content = await file.read()
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Create database record
    guest_image = GuestImage(
        guest_id=guest_id,
        image_type=image_type,
        file_path=file_path,
        file_name=safe_filename,
        file_size=len(file_content),
        mime_type=file.content_type,
        uploaded_by_user_id=current_user.get("id"),
    )
    db.add(guest_image)
    db.commit()
    db.refresh(guest_image)

    return guest_image.to_dict()


# ============== GET GUEST PHOTOS ==============

@router.get("/{guest_id}/photos", response_model=list[GuestImageResponse])
async def get_guest_photos(
    guest_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all ID photos for a specific guest.

    **Parameters:**
    - guest_id: Guest ID

    **Returns:** List of guest's uploaded ID photos with metadata
    """
    # Verify guest exists
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {guest_id} not found")

    # Get all images for guest
    images = db.query(GuestImage).filter(GuestImage.guest_id == guest_id).all()

    return [img.to_dict() for img in images]


# ============== DELETE GUEST PHOTO ==============

@router.delete("/{guest_id}/photos/{photo_id}")
async def delete_guest_photo(
    guest_id: int,
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a guest's ID photo.

    **Parameters:**
    - guest_id: Guest ID
    - photo_id: Photo ID to delete

    **Returns:** Confirmation message
    """
    # Verify guest exists
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest with ID {guest_id} not found")

    # Get photo
    photo = db.query(GuestImage).filter(
        and_(GuestImage.id == photo_id, GuestImage.guest_id == guest_id)
    ).first()

    if not photo:
        raise HTTPException(status_code=404, detail=f"Photo with ID {photo_id} not found for guest {guest_id}")

    # Delete file from storage
    try:
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Could not delete file {photo.file_path}: {str(e)}")

    # Delete from database
    db.delete(photo)
    db.commit()

    return {"message": f"Photo {photo_id} deleted successfully"}
