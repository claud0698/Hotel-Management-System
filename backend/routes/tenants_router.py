"""
Tenant management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from models import Tenant, Room, RoomHistory
from schemas import TenantCreate, TenantUpdate, TenantResponse
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
    # Parse move_in_date
    move_in_date = None
    if tenant_data.move_in_date:
        move_in_date = datetime.fromisoformat(tenant_data.move_in_date)

    # Create tenant
    tenant = Tenant(
        name=tenant_data.name,
        phone=tenant_data.phone,
        email=tenant_data.email,
        id_number=tenant_data.id_number,
        move_in_date=move_in_date,
        current_room_id=tenant_data.current_room_id,
        status=tenant_data.status,
        notes=tenant_data.notes
    )

    db.add(tenant)
    db.flush()

    # Create room history and update room status if room is assigned
    if tenant.current_room_id:
        room_history = RoomHistory(
            room_id=tenant.current_room_id,
            tenant_id=tenant.id,
            move_in_date=move_in_date or datetime.utcnow()
        )
        db.add(room_history)

        room = db.query(Room).filter(Room.id == tenant.current_room_id).first()
        if room:
            room.status = 'occupied'

    db.commit()
    db.refresh(tenant)

    return {
        "message": "Tenant created",
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

    # Update fields
    update_data = tenant_data.model_dump(exclude_unset=True)

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
                    old_history.move_out_date = datetime.utcnow()

        # Update new room status
        if new_room_id:
            new_room = db.query(Room).filter(Room.id == new_room_id).first()
            if new_room:
                new_room.status = 'occupied'
                new_history = RoomHistory(
                    room_id=new_room_id,
                    tenant_id=tenant_id,
                    move_in_date=datetime.utcnow()
                )
                db.add(new_history)

    # Handle date fields
    if 'move_in_date' in update_data and update_data['move_in_date']:
        update_data['move_in_date'] = datetime.fromisoformat(update_data['move_in_date'])

    # Update tenant
    for field, value in update_data.items():
        if field not in ['move_in_date', 'current_room_id']:
            setattr(tenant, field, value)
        elif field == 'move_in_date':
            tenant.move_in_date = value
        elif field == 'current_room_id':
            tenant.current_room_id = value

    db.commit()
    db.refresh(tenant)

    return {
        "message": "Tenant updated",
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
