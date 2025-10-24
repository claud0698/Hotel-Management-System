"""
Tenant management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from models import Tenant, Room, RoomHistory
from schemas import TenantCreate, TenantUpdate, TenantResponse
from security import get_current_user
from validators import (
    validate_tenant_name,
    validate_tenant_status,
    validate_email,
    validate_phone,
    validate_date
)

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
async def get_tenants(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tenants"""
    tenants = db.query(Tenant).all()
    return {
        "tenants": [tenant.to_dict() for tenant in tenants]
    }


@router.get("/{tenant_id}", response_model=dict)
async def get_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    return {"tenant": tenant.to_dict()}


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new tenant"""
    # Validate inputs
    try:
        validated_name = validate_tenant_name(tenant_data.name)
        validated_status = validate_tenant_status(tenant_data.status)
        validated_email = validate_email(tenant_data.email)
        validated_phone = validate_phone(tenant_data.phone)
        validated_move_in = validate_date(tenant_data.move_in_date, "Move-in date") if tenant_data.move_in_date else None
    except HTTPException as e:
        raise e

    # Create tenant
    tenant = Tenant(
        name=validated_name,
        phone=validated_phone,
        email=validated_email,
        id_number=tenant_data.id_number,
        move_in_date=validated_move_in,
        current_room_id=tenant_data.current_room_id,
        status=validated_status,
        notes=tenant_data.notes
    )

    db.add(tenant)
    db.flush()

    # Create room history and update room status if room is assigned
    if tenant.current_room_id:
        # Verify room exists
        room = db.query(Room).filter(Room.id == tenant.current_room_id).first()
        if not room:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with ID {tenant.current_room_id} not found"
            )

        room_history = RoomHistory(
            room_id=tenant.current_room_id,
            tenant_id=tenant.id,
            move_in_date=validated_move_in or datetime.now(timezone.utc)
        )
        db.add(room_history)
        room.status = 'occupied'

    db.commit()
    db.refresh(tenant)

    return {
        "message": "Tenant created successfully",
        "tenant": tenant.to_dict()
    }


@router.put("/{tenant_id}", response_model=dict)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Validate only provided fields
    try:
        update_data = tenant_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            update_data["name"] = validate_tenant_name(update_data["name"])

        if "status" in update_data:
            update_data["status"] = validate_tenant_status(update_data["status"])

        if "email" in update_data:
            update_data["email"] = validate_email(update_data["email"])

        if "phone" in update_data:
            update_data["phone"] = validate_phone(update_data["phone"])

        if "move_in_date" in update_data and update_data["move_in_date"]:
            update_data["move_in_date"] = validate_date(update_data["move_in_date"], "Move-in date")
    except HTTPException as e:
        raise e

    # Handle room assignment changes
    if 'current_room_id' in update_data and update_data['current_room_id'] != tenant.current_room_id:
        old_room_id = tenant.current_room_id
        new_room_id = update_data['current_room_id']

        # Update old room status
        if old_room_id:
            old_room = db.query(Room).filter(Room.id == old_room_id).first()
            if old_room:
                old_room.status = 'available'
                # Update room history
                old_history = db.query(RoomHistory).filter(
                    RoomHistory.room_id == old_room_id,
                    RoomHistory.tenant_id == tenant_id,
                    RoomHistory.move_out_date == None
                ).first()
                if old_history:
                    old_history.move_out_date = datetime.now(timezone.utc)

        # Update new room status
        if new_room_id:
            new_room = db.query(Room).filter(Room.id == new_room_id).first()
            if new_room:
                new_room.status = 'occupied'
                new_history = RoomHistory(
                    room_id=new_room_id,
                    tenant_id=tenant_id,
                    move_in_date=datetime.now(timezone.utc)
                )
                db.add(new_history)

    # Update tenant
    for field, value in update_data.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)

    return {
        "message": "Tenant updated successfully",
        "tenant": tenant.to_dict()
    }


@router.delete("/{tenant_id}", response_model=dict)
async def delete_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Update room status if tenant has a room
    if tenant.current_room_id:
        room = db.query(Room).filter(Room.id == tenant.current_room_id).first()
        if room:
            room.status = 'available'

    db.delete(tenant)
    db.commit()

    return {"message": "Tenant deleted"}
